variable "storage_account_id" {
  description = "Resource ID of the ADLS Gen2 storage account."
  type        = string
}

variable "compute_principal_id" {
  description = "Principal ID of the AML compute cluster managed identity."
  type        = string
}
