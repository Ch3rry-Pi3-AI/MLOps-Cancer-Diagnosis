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

data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

resource "random_pet" "aml" {
  length    = 2
  separator = "-"
}

locals {
  workspace_name_raw = var.workspace_name != null ? var.workspace_name : "${var.workspace_name_prefix}-${random_pet.aml.id}"
  workspace_name_sanitized = replace(lower(local.workspace_name_raw), "_", "-")
  workspace_name = substr(local.workspace_name_sanitized, 0, 33)
}

resource "azurerm_machine_learning_workspace" "main" {
  name                          = local.workspace_name
  location                      = coalesce(var.location, data.azurerm_resource_group.main.location)
  resource_group_name           = data.azurerm_resource_group.main.name
  application_insights_id       = var.application_insights_id
  key_vault_id                  = var.key_vault_id
  storage_account_id            = var.storage_account_id
  container_registry_id         = var.container_registry_id
  public_network_access_enabled = var.public_network_access_enabled

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}
