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

resource "random_pet" "law" {
  length    = 2
  separator = "-"
}

resource "random_pet" "appi" {
  length    = 2
  separator = "-"
}

locals {
  log_analytics_name = var.log_analytics_name != null ? var.log_analytics_name : "${var.log_analytics_name_prefix}-${random_pet.law.id}"
  app_insights_name  = var.app_insights_name != null ? var.app_insights_name : "${var.app_insights_name_prefix}-${random_pet.appi.id}"
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = local.log_analytics_name
  location            = coalesce(var.location, data.azurerm_resource_group.main.location)
  resource_group_name = data.azurerm_resource_group.main.name
  sku                 = var.sku
  retention_in_days   = var.retention_in_days

  tags = var.tags
}

resource "azurerm_application_insights" "main" {
  name                = local.app_insights_name
  location            = azurerm_log_analytics_workspace.main.location
  resource_group_name = data.azurerm_resource_group.main.name
  application_type    = var.application_type
  workspace_id        = azurerm_log_analytics_workspace.main.id

  tags = var.tags
}
