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

data "azurerm_client_config" "current" {}

resource "random_pet" "kv" {
  length    = 2
  separator = ""
}

locals {
  key_vault_name = lower(var.key_vault_name != null ? var.key_vault_name : substr("${var.key_vault_name_prefix}${random_pet.kv.id}", 0, 24))
}

resource "azurerm_key_vault" "main" {
  name                        = local.key_vault_name
  location                    = coalesce(var.location, data.azurerm_resource_group.main.location)
  resource_group_name         = data.azurerm_resource_group.main.name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = var.sku_name
  enable_rbac_authorization   = var.enable_rbac_authorization
  public_network_access_enabled = var.public_network_access_enabled
  soft_delete_retention_days  = var.soft_delete_retention_days
  purge_protection_enabled    = var.purge_protection_enabled

  tags = var.tags
}

resource "azurerm_role_assignment" "key_vault_admin" {
  count = var.key_vault_admin_object_id != null ? 1 : 0

  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Administrator"
  principal_id         = var.key_vault_admin_object_id
}
