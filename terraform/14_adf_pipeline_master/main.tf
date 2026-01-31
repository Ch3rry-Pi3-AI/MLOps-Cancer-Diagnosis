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

locals {
  pipeline_name = var.pipeline_name != null ? var.pipeline_name : "${var.pipeline_name_prefix}-${random_pet.pipeline.id}"

  pipeline_body = {
    properties = {
      activities = [
        {
          name = "run_ingest_bronze"
          type = "ExecutePipeline"
          typeProperties = {
            pipeline = {
              referenceName = var.ingest_pipeline_name
              type          = "PipelineReference"
            }
            waitOnCompletion = true
          }
        },
        {
          name = "run_bronze_to_silver"
          type = "ExecutePipeline"
          dependsOn = [
            {
              activity             = "run_ingest_bronze"
              dependencyConditions = ["Succeeded"]
            }
          ]
          typeProperties = {
            pipeline = {
              referenceName = var.silver_pipeline_name
              type          = "PipelineReference"
            }
            waitOnCompletion = true
          }
        },
        {
          name = "run_silver_to_gold"
          type = "ExecutePipeline"
          dependsOn = [
            {
              activity             = "run_bronze_to_silver"
              dependencyConditions = ["Succeeded"]
            }
          ]
          typeProperties = {
            pipeline = {
              referenceName = var.gold_pipeline_name
              type          = "PipelineReference"
            }
            waitOnCompletion = true
          }
        }
      ]
      annotations = []
    }
  }
}

resource "azapi_resource" "pipeline" {
  type                      = "Microsoft.DataFactory/factories/pipelines@2018-06-01"
  name                      = local.pipeline_name
  parent_id                 = var.data_factory_id
  body                      = jsonencode(local.pipeline_body)
  schema_validation_enabled = false
}
