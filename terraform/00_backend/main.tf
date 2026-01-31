terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
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

resource "random_pet" "backend" {
  length    = 2
  separator = "-"
}

resource "random_string" "storage_suffix" {
  length  = 6
  upper   = false
  lower   = true
  number  = true
  special = false
}

locals {
  resource_group_name = var.backend_resource_group_name != null ? var.backend_resource_group_name : "${var.backend_resource_group_name_prefix}-${random_pet.backend.id}"
  storage_account_name = var.storage_account_name != null ? var.storage_account_name : substr("${var.storage_account_name_prefix}${random_string.storage_suffix.result}", 0, 24)
}

resource "azurerm_resource_group" "backend" {
  name     = local.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "backend" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.backend.name
  location                 = azurerm_resource_group.backend.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_blob_public_access = false
  min_tls_version          = "TLS1_2"
}

resource "azurerm_storage_container" "backend" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.backend.name
  container_access_type = "private"
}
