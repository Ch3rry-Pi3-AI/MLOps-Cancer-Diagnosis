variable "data_factory_id" {
  type        = string
  description = "Data Factory ID that owns the pipeline"
}

variable "http_linked_service_name" {
  type        = string
  description = "HTTP linked service name"
}

variable "adls_linked_service_name" {
  type        = string
  description = "ADLS Gen2 linked service name"
}

variable "pipeline_name" {
  type        = string
  description = "Pipeline name (if null, uses pipeline_name_prefix + random suffix)"
  default     = null
}

variable "pipeline_name_prefix" {
  type        = string
  description = "Prefix used to build the pipeline name when pipeline_name is null"
  default     = "pl-mlops-cancer-http"
}

variable "http_dataset_name" {
  type        = string
  description = "HTTP dataset name (if null, uses http_dataset_name_prefix + random suffix)"
  default     = null
}

variable "http_dataset_name_prefix" {
  type        = string
  description = "Prefix used to build the HTTP dataset name when http_dataset_name is null"
  default     = "ds_http_mlopscancer"
}

variable "sink_dataset_name" {
  type        = string
  description = "ADLS sink dataset name (if null, uses sink_dataset_name_prefix + random suffix)"
  default     = null
}

variable "sink_dataset_name_prefix" {
  type        = string
  description = "Prefix used to build the sink dataset name when sink_dataset_name is null"
  default     = "ds_adls_bronze_mlopscancer"
}

variable "http_relative_url" {
  type        = string
  description = "Relative URL for the raw dataset in GitHub"
  default     = "Ch3rry-Pi3-AI/MLOps-Cancer-Diagnosis/refs/heads/main/data/breast-cancer.data"
}

variable "sink_file_system" {
  type        = string
  description = "ADLS Gen2 file system (container) for landing the raw file"
  default     = "bronze"
}

variable "sink_folder" {
  type        = string
  description = "Folder path within the container"
  default     = "breast_cancer/raw"
}

variable "sink_file" {
  type        = string
  description = "Output file name"
  default     = "breast_cancer.csv"
}
