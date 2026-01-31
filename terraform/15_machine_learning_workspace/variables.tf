variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group"
}

variable "location" {
  type        = string
  description = "Azure region for the AML workspace (defaults to RG location if null)"
  default     = null
}

variable "workspace_name" {
  type        = string
  description = "AML workspace name (if null, uses workspace_name_prefix + random suffix)"
  default     = null
}

variable "workspace_name_prefix" {
  type        = string
  description = "Prefix used to build the AML workspace name when workspace_name is null"
  default     = "mlw-mlops-cancer"
}

variable "storage_account_id" {
  type        = string
  description = "Storage account ID for AML workspace"
}

variable "key_vault_id" {
  type        = string
  description = "Key Vault ID for AML workspace"
}

variable "application_insights_id" {
  type        = string
  description = "Application Insights ID for AML workspace"
}

variable "container_registry_id" {
  type        = string
  description = "Container Registry ID for AML workspace"
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Allow public network access to AML workspace"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to the AML workspace"
  default     = {}
}
