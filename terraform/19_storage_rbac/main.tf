terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_role_assignment" "storage_blob_contributor" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.compute_principal_id
  skip_service_principal_aad_check = true
  name                 = uuidv5("6ba7b810-9dad-11d1-80b4-00c04fd430c8", "${var.storage_account_id}|${var.compute_principal_id}")
}
