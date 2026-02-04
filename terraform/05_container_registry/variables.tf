variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group"
}

variable "location" {
  type        = string
  description = "Azure region for the container registry (defaults to RG location if null)"
  default     = null
}

variable "acr_name" {
  type        = string
  description = "ACR name (if null, uses acr_name_prefix + random suffix)"
  default     = null
}

variable "acr_name_prefix" {
  type        = string
  description = "Prefix used to build the ACR name when acr_name is null"
  default     = "acrmlopscancer"
}

variable "sku" {
  type        = string
  description = "ACR SKU"
  default     = "Basic"
}

variable "admin_enabled" {
  type        = bool
  description = "Enable admin user"
  default     = false
}

variable "public_network_access_enabled" {
  type        = bool
  description = "Allow public network access to ACR"
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to the ACR"
  default     = {}
}
