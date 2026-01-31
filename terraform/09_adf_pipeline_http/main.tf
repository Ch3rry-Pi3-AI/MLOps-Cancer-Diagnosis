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

resource "random_pet" "pipeline" {
  length    = 2
  separator = "-"
}

resource "random_pet" "http_dataset" {
  length    = 2
  separator = "_"
}

resource "random_pet" "sink_dataset" {
  length    = 2
  separator = "_"
}

locals {
  http_dataset_prefix = replace(var.http_dataset_name_prefix, "-", "_")
  sink_dataset_prefix = replace(var.sink_dataset_name_prefix, "-", "_")

  pipeline_name     = var.pipeline_name != null ? var.pipeline_name : "${var.pipeline_name_prefix}-${random_pet.pipeline.id}"
  http_dataset_name = var.http_dataset_name != null ? var.http_dataset_name : "${local.http_dataset_prefix}_${random_pet.http_dataset.id}"
  sink_dataset_name = var.sink_dataset_name != null ? var.sink_dataset_name : "${local.sink_dataset_prefix}_${random_pet.sink_dataset.id}"

  schema_columns = [
    "class",
    "age",
    "menopause",
    "tumor_size",
    "inv_nodes",
    "node_caps",
    "deg_malig",
    "breast",
    "breast_quad",
    "irradiat",
  ]

  source_schema_columns = [for idx in range(length(local.schema_columns)) : "Prop_${idx}"]

  source_schema = [for name in local.source_schema_columns : {
    name = name
    type = "String"
  }]

  sink_schema = [for name in local.schema_columns : {
    name = name
    type = "String"
  }]

  http_dataset_params = {
    p_rel_url = "@pipeline().parameters.p_rel_url"
  }

  sink_dataset_params = {
    p_sink_folder = "@pipeline().parameters.p_sink_folder"
    p_sink_file   = "@pipeline().parameters.p_sink_file"
  }

  column_mappings = [
    for idx, name in local.schema_columns : {
      source = {
        name = "Prop_${idx}"
      }
      sink = {
        name = name
      }
    }
  ]

  pipeline_body = {
    properties = {
      activities = [
        {
          name = "copy_http_to_adls"
          type = "Copy"
          inputs = [
            {
              referenceName = azapi_resource.http_dataset.name
              type          = "DatasetReference"
              parameters    = local.http_dataset_params
            }
          ]
          outputs = [
            {
              referenceName = azapi_resource.adls_sink_dataset.name
              type          = "DatasetReference"
              parameters    = local.sink_dataset_params
            }
          ]
          typeProperties = {
            source = {
              type = "DelimitedTextSource"
            }
            sink = {
              type = "DelimitedTextSink"
            }
            translator = {
              type     = "TabularTranslator"
              mappings = local.column_mappings
            }
          }
        }
      ]
      parameters = {
        p_rel_url = {
          type         = "String"
          defaultValue = var.http_relative_url
        }
        p_sink_folder = {
          type         = "String"
          defaultValue = var.sink_folder
        }
        p_sink_file = {
          type         = "String"
          defaultValue = var.sink_file
        }
      }
      annotations = []
    }
  }
}

resource "azapi_resource" "http_dataset" {
  type                      = "Microsoft.DataFactory/factories/datasets@2018-06-01"
  name                      = local.http_dataset_name
  parent_id                 = var.data_factory_id
  schema_validation_enabled = false

  body = jsonencode({
    properties = {
      linkedServiceName = {
        referenceName = var.http_linked_service_name
        type          = "LinkedServiceReference"
      }
      parameters = {
        p_rel_url = {
          type = "String"
        }
      }
      type = "DelimitedText"
      schema = local.source_schema
      typeProperties = {
        location = {
          type        = "HttpServerLocation"
          relativeUrl = "@{dataset().p_rel_url}"
        }
        columnDelimiter  = ","
        rowDelimiter     = "\n"
        firstRowAsHeader = false
        quoteChar        = "\""
        escapeChar       = "\\"
        encodingName     = "utf-8"
      }
    }
  })
}

resource "azapi_resource" "adls_sink_dataset" {
  type                      = "Microsoft.DataFactory/factories/datasets@2018-06-01"
  name                      = local.sink_dataset_name
  parent_id                 = var.data_factory_id
  schema_validation_enabled = false

  body = jsonencode({
    properties = {
      linkedServiceName = {
        referenceName = var.adls_linked_service_name
        type          = "LinkedServiceReference"
      }
      parameters = {
        p_sink_folder = {
          type = "String"
        }
        p_sink_file = {
          type = "String"
        }
      }
      type = "DelimitedText"
      schema = local.sink_schema
      typeProperties = {
        location = {
          type       = "AzureBlobFSLocation"
          fileSystem = var.sink_file_system
          folderPath = "@{dataset().p_sink_folder}"
          fileName   = "@{dataset().p_sink_file}"
        }
        columnDelimiter  = ","
        rowDelimiter     = "\n"
        firstRowAsHeader = true
        quoteChar        = "\""
        escapeChar       = "\\"
        encodingName     = "utf-8"
      }
    }
  })
}

resource "azapi_resource" "pipeline" {
  type                      = "Microsoft.DataFactory/factories/pipelines@2018-06-01"
  name                      = local.pipeline_name
  parent_id                 = var.data_factory_id
  body                      = jsonencode(local.pipeline_body)
  schema_validation_enabled = false

  depends_on = [
    azapi_resource.http_dataset,
    azapi_resource.adls_sink_dataset,
  ]
}
