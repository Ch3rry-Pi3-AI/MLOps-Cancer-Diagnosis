variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group"
}

variable "location" {
  type        = string
  description = "Azure region for the VNet (defaults to RG location if null)"
  default     = null
}

variable "vnet_name" {
  type        = string
  description = "Virtual network name (if null, uses vnet_name_prefix + random suffix)"
  default     = null
}

variable "vnet_name_prefix" {
  type        = string
  description = "Prefix used to build the VNet name when vnet_name is null"
  default     = "vnet-mlops-cancer"
}

variable "address_space" {
  type        = list(string)
  description = "Address space for the VNet"
  default     = ["10.40.0.0/16"]
}

variable "subnet_prefixes" {
  type        = map(string)
  description = "Subnet name to address prefix mapping"
  default = {
    default           = "10.40.1.0/24"
    private_endpoints = "10.40.2.0/24"
    aml               = "10.40.3.0/24"
    adf               = "10.40.4.0/24"
  }
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to the VNet and subnets"
  default     = {}
}
