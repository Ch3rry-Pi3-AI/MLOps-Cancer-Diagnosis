variable "resource_group_name" {
  type        = string
  description = "Name of the existing resource group"
}

variable "location" {
  type        = string
  description = "Azure region for Log Analytics (defaults to RG location if null)"
  default     = null
}

variable "log_analytics_name" {
  type        = string
  description = "Log Analytics workspace name (if null, uses log_analytics_name_prefix + random suffix)"
  default     = null
}

variable "log_analytics_name_prefix" {
  type        = string
  description = "Prefix used to build the Log Analytics name when log_analytics_name is null"
  default     = "law-mlops-cancer"
}

variable "sku" {
  type        = string
  description = "Log Analytics SKU"
  default     = "PerGB2018"
}

variable "retention_in_days" {
  type        = number
  description = "Log Analytics retention in days"
  default     = 30
}

variable "app_insights_name" {
  type        = string
  description = "Application Insights name (if null, uses app_insights_name_prefix + random suffix)"
  default     = null
}

variable "app_insights_name_prefix" {
  type        = string
  description = "Prefix used to build the Application Insights name when app_insights_name is null"
  default     = "appi-mlops-cancer"
}

variable "application_type" {
  type        = string
  description = "Application Insights type"
  default     = "web"
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to Log Analytics and Application Insights"
  default     = {}
}
