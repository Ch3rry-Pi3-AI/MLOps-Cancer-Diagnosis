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

  bronze_source_dataset_name = var.bronze_source_dataset_name != null ? var.bronze_source_dataset_name : "${var.bronze_source_dataset_name_prefix}_${random_pet.dataset.id}"

  dataflow_script_lines = [
    "source(output(class as string, age as string, menopause as string, tumor_size as string, inv_nodes as string, node_caps as string, deg_malig as string, breast as string, breast_quad as string, irradiat as string), allowSchemaDrift: true, validateSchema: false, ignoreNoFilesFound: false, format: 'delimited') ~> srcBronze",
    "srcBronze derive(class = iif(class == '?', toString(null()), class), age = iif(age == '?', toString(null()), age), menopause = iif(menopause == '?', toString(null()), menopause), tumor_size = iif(tumor_size == '?', toString(null()), tumor_size), inv_nodes = iif(inv_nodes == '?', toString(null()), inv_nodes), node_caps = iif(node_caps == '?', toString(null()), node_caps), deg_malig = iif(deg_malig == '?', toString(null()), deg_malig), breast = iif(breast == '?', toString(null()), breast), breast_quad = iif(breast_quad == '?', toString(null()), replace(breast_quad, '_', '-')), irradiat = iif(irradiat == '?', toString(null()), irradiat)) ~> drClean",
    "drClean aggregate(groupBy(class, age, menopause, tumor_size, inv_nodes, node_caps, deg_malig, breast, breast_quad, irradiat)) ~> agDistinct",
    "agDistinct sink(allowSchemaDrift: true, validateSchema: false, store: 'AzureBlobFS', format: '${var.sink_format}', fileSystem: '${var.sink_container}', folderPath: '${var.sink_folder}') ~> sinkSilver",
  ]

  dataflow_body = {
    properties = {
      type = "MappingDataFlow"
      typeProperties = {
        sources = [
          {
            name = "srcBronze"
            dataset = {
              referenceName = azurerm_data_factory_dataset_delimited_text.bronze_source.name
              type          = "DatasetReference"
            }
          }
        ]
        transformations = [
          { name = "drClean" },
          { name = "agDistinct" },
        ]
        sinks = [
          {
            name = "sinkSilver"
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

resource "azurerm_data_factory_dataset_delimited_text" "bronze_source" {
  name                = local.bronze_source_dataset_name
  data_factory_id     = var.data_factory_id
  linked_service_name = var.adls_linked_service_name

  column_delimiter    = ","
  row_delimiter       = "\n"
  first_row_as_header = true
  encoding            = "UTF-8"

  azure_blob_fs_location {
    file_system = var.source_container
    path        = var.source_folder
    filename    = var.source_file
  }
}

resource "azapi_resource" "dataflow" {
  type                      = "Microsoft.DataFactory/factories/dataflows@2018-06-01"
  name                      = local.dataflow_name
  parent_id                 = var.data_factory_id
  body                      = jsonencode(local.dataflow_body)
  schema_validation_enabled = false

  depends_on = [
    azurerm_data_factory_dataset_delimited_text.bronze_source,
  ]
}
