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

resource "random_pet" "http" {
  length    = 2
  separator = "-"
}

resource "random_pet" "adls" {
  length    = 2
  separator = "-"
}

locals {
  http_linked_service_name = var.http_linked_service_name != null ? var.http_linked_service_name : "${var.http_linked_service_name_prefix}-${random_pet.http.id}"
  adls_linked_service_name = var.adls_linked_service_name != null ? var.adls_linked_service_name : "${var.adls_linked_service_name_prefix}-${random_pet.adls.id}"
  http_properties = merge(
    {
      type = "HttpServer"
      typeProperties = {
        url                                 = var.http_base_url
        authenticationType                 = var.http_authentication_type
        enableServerCertificateValidation = var.http_enable_certificate_validation
      }
      description = var.description
    },
    var.integration_runtime_name != null ? {
      connectVia = {
        referenceName = var.integration_runtime_name
        type          = "IntegrationRuntimeReference"
      }
    } : {}
  )
}

resource "azapi_resource" "http" {
  type                      = "Microsoft.DataFactory/factories/linkedservices@2018-06-01"
  name                      = local.http_linked_service_name
  parent_id                 = var.data_factory_id
  schema_validation_enabled = false

  body = jsonencode({
    properties = local.http_properties
  })
}

resource "azurerm_data_factory_linked_service_data_lake_storage_gen2" "adls" {
  name            = local.adls_linked_service_name
  data_factory_id = var.data_factory_id

  url                 = var.storage_dfs_endpoint
  storage_account_key = var.storage_account_key
  description         = var.description
}
