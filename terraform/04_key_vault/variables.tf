variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group"
}

variable "location" {
  type        = string
  description = "Azure region for the key vault (defaults to RG location if null)"
  default     = null
}

variable "key_vault_name" {
  type        = string
  description = "Key Vault name (if null, uses key_vault_name_prefix + random suffix)"
  default     = null
}

variable "key_vault_name_prefix" {
  type        = string
  description = "Prefix used to build the Key Vault name when key_vault_name is null"
  default     = "kvmlopscancer"
}

variable "sku_name" {
  type        = string
  description = "Key Vault SKU name"
  default     = "standard"
}

variable "enable_rbac_authorization" {
  type        = bool
  description = "Enable RBAC authorization for Key Vault"
  default     = true
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Allow public network access to Key Vault"
  default     = true
}

variable "soft_delete_retention_days" {
  type        = number
  description = "Soft delete retention days"
  default     = 7
}

variable "purge_protection_enabled" {
  type        = bool
  description = "Enable purge protection"
  default     = false
}

variable "key_vault_admin_object_id" {
  type        = string
  description = "Optional object ID to grant Key Vault Administrator"
  default     = null
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to Key Vault"
  default     = {}
}
