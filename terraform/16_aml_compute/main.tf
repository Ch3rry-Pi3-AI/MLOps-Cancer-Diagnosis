terraform {
  required_version = ">= 1.5"

  required_providers {
    azapi = {
      source  = "azure/azapi"
      version = "~> 1.13"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azapi" {}
provider "azurerm" {
  features {}
}

resource "azapi_resource" "main" {
  type      = "Microsoft.MachineLearningServices/workspaces/computes@2023-04-01"
  name      = var.compute_name
  parent_id = var.workspace_id
  location  = var.location
  tags      = var.tags

  identity {
    type = "SystemAssigned"
  }

  body = jsonencode({
    properties = {
      computeType = "AmlCompute"
      properties = {
        vmSize       = var.vm_size
        vmPriority   = var.vm_priority
        scaleSettings = {
          minNodeCount               = var.min_instances
          maxNodeCount               = var.max_instances
          nodeIdleTimeBeforeScaleDown = var.idle_time_before_scaledown
        }
      }
    }
  })
}
