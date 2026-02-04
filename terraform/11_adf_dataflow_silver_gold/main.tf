terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.13"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "azapi" {}

resource "random_pet" "dataflow" {
  length    = 2
  separator = "-"
}

resource "random_pet" "dataset" {
  length    = 2
  separator = "_"
}

locals {
  dataflow_name = var.dataflow_name != null ? var.dataflow_name : "${var.dataflow_name_prefix}-${random_pet.dataflow.id}"
  silver_source_dataset_name = var.silver_source_dataset_name != null ? var.silver_source_dataset_name : "${var.silver_source_dataset_name_prefix}_${random_pet.dataset.id}"

  dataflow_script_lines = [
    "source(output(class as string, age as string, menopause as string, tumor_size as string, inv_nodes as string, node_caps as string, deg_malig as string, breast as string, breast_quad as string, irradiat as string), allowSchemaDrift: true, validateSchema: false, ignoreNoFilesFound: false, format: 'parquet') ~> srcSilver",
    "srcSilver derive(label = iif(class == 'recurrence-events', toInteger(1), iif(class == 'no-recurrence-events', toInteger(0), toInteger(null()))), age_mid = iif(isNull(age), toDouble(null()), (toDouble(split(age,'-')[0]) + toDouble(split(age,'-')[1])) / 2.0), tumor_size_mid = iif(isNull(tumor_size), toDouble(null()), (toDouble(split(tumor_size,'-')[0]) + toDouble(split(tumor_size,'-')[1])) / 2.0), inv_nodes_mid = iif(isNull(inv_nodes), toDouble(null()), (toDouble(split(inv_nodes,'-')[0]) + toDouble(split(inv_nodes,'-')[1])) / 2.0), deg_malig_num = iif(isNull(deg_malig), toInteger(null()), toInteger(deg_malig)), node_caps_num = iif(node_caps == 'yes', toInteger(1), iif(node_caps == 'no', toInteger(0), toInteger(null()))), irradiat_num = iif(irradiat == 'yes', toInteger(1), iif(irradiat == 'no', toInteger(0), toInteger(null()))), breast_right = iif(breast == 'right', toInteger(1), iif(breast == 'left', toInteger(0), toInteger(null()))), menopause_lt40 = iif(menopause == 'lt40', toInteger(1), toInteger(0)), menopause_ge40 = iif(menopause == 'ge40', toInteger(1), toInteger(0)), menopause_premeno = iif(menopause == 'premeno', toInteger(1), toInteger(0)), breast_quad_left_up = iif(breast_quad == 'left-up', toInteger(1), toInteger(0)), breast_quad_left_low = iif(breast_quad == 'left-low', toInteger(1), toInteger(0)), breast_quad_right_up = iif(breast_quad == 'right-up', toInteger(1), toInteger(0)), breast_quad_right_low = iif(breast_quad == 'right-low', toInteger(1), toInteger(0)), breast_quad_central = iif(breast_quad == 'central', toInteger(1), toInteger(0))) ~> drEncode",
    "drEncode derive(age_mid = iif(isNull(age_mid), toDouble(0.0), age_mid), tumor_size_mid = iif(isNull(tumor_size_mid), toDouble(0.0), tumor_size_mid), inv_nodes_mid = iif(isNull(inv_nodes_mid), toDouble(0.0), inv_nodes_mid), deg_malig_num = iif(isNull(deg_malig_num), toInteger(0), deg_malig_num), node_caps_num = iif(isNull(node_caps_num), toInteger(0), node_caps_num), irradiat_num = iif(isNull(irradiat_num), toInteger(0), irradiat_num), breast_right = iif(isNull(breast_right), toInteger(0), breast_right), menopause_lt40 = iif(isNull(menopause_lt40), toInteger(0), menopause_lt40), menopause_ge40 = iif(isNull(menopause_ge40), toInteger(0), menopause_ge40), menopause_premeno = iif(isNull(menopause_premeno), toInteger(0), menopause_premeno), breast_quad_left_up = iif(isNull(breast_quad_left_up), toInteger(0), breast_quad_left_up), breast_quad_left_low = iif(isNull(breast_quad_left_low), toInteger(0), breast_quad_left_low), breast_quad_right_up = iif(isNull(breast_quad_right_up), toInteger(0), breast_quad_right_up), breast_quad_right_low = iif(isNull(breast_quad_right_low), toInteger(0), breast_quad_right_low), breast_quad_central = iif(isNull(breast_quad_central), toInteger(0), breast_quad_central)) ~> drImpute",
    "drImpute filter(!isNull(label)) ~> fltLabel",
    "fltLabel select(mapColumn(label, age_mid, tumor_size_mid, inv_nodes_mid, deg_malig_num, node_caps_num, irradiat_num, breast_right, menopause_lt40, menopause_ge40, menopause_premeno, breast_quad_left_up, breast_quad_left_low, breast_quad_right_up, breast_quad_right_low, breast_quad_central)) ~> selGold",
    "selGold sink(allowSchemaDrift: true, validateSchema: false, store: 'AzureBlobFS', format: '${var.sink_format}', fileSystem: '${var.sink_container}', folderPath: '${var.sink_folder}') ~> sinkGold",
  ]

  dataflow_body = {
    properties = {
      type = "MappingDataFlow"
      typeProperties = {
        sources = [
          {
            name = "srcSilver"
            dataset = {
              referenceName = azurerm_data_factory_dataset_parquet.silver_source.name
              type          = "DatasetReference"
            }
          }
        ]
        transformations = [
          { name = "drEncode" },
          { name = "drImpute" },
          { name = "fltLabel" },
          { name = "selGold" },
        ]
        sinks = [
          {
            name = "sinkGold"
            linkedService = {
              referenceName = var.adls_linked_service_name
              type          = "LinkedServiceReference"
            }
          }
        ]
        scriptLines = local.dataflow_script_lines
      }
    }
  }
}

resource "azurerm_data_factory_dataset_parquet" "silver_source" {
  name                = local.silver_source_dataset_name
  data_factory_id     = var.data_factory_id
  linked_service_name = var.adls_linked_service_name

  azure_blob_fs_location {
    file_system = var.source_container
    path        = var.source_folder
  }
}

resource "azapi_resource" "dataflow" {
  type                      = "Microsoft.DataFactory/factories/dataflows@2018-06-01"
  name                      = local.dataflow_name
  parent_id                 = var.data_factory_id
  body                      = jsonencode(local.dataflow_body)
  schema_validation_enabled = false

  depends_on = [
    azurerm_data_factory_dataset_parquet.silver_source,
  ]
}
