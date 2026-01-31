variable "backend_resource_group_name" {
  type        = string
  default     = null
  description = "Resource group name for Terraform state (if null, uses prefix + random suffix)."
}

variable "backend_resource_group_name_prefix" {
  type        = string
  default     = "rg-mlops-cancer-tfstate"
  description = "Prefix used to build the backend resource group name when backend_resource_group_name is null."
}

variable "location" {
  type        = string
  default     = "eastus2"
  description = "Azure region for the backend resources."
}

variable "storage_account_name" {
  type        = string
  default     = null
  description = "Storage account name for Terraform state (if null, uses prefix + random suffix)."
}

variable "storage_account_name_prefix" {
  type        = string
  default     = "stmlopstfstate"
  description = "Prefix used to build the backend storage account name when storage_account_name is null."
}

variable "container_name" {
  type        = string
  default     = "tfstate"
  description = "Storage container name for Terraform state."
}
