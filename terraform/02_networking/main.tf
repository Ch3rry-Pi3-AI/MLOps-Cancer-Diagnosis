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

resource "random_pet" "vnet" {
  length    = 2
  separator = "-"
}

locals {
  vnet_name = var.vnet_name != null ? var.vnet_name : "${var.vnet_name_prefix}-${random_pet.vnet.id}"
}

resource "azurerm_virtual_network" "main" {
  name                = local.vnet_name
  address_space       = var.address_space
  location            = coalesce(var.location, data.azurerm_resource_group.main.location)
  resource_group_name = data.azurerm_resource_group.main.name

  tags = var.tags
}

resource "azurerm_subnet" "main" {
  for_each = var.subnet_prefixes

  name                 = each.key
  resource_group_name  = data.azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = [each.value]
}
