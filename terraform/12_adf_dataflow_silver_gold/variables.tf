variable "data_factory_id" {
  type        = string
  description = "Data Factory ID that owns the data flow"
}

variable "adls_linked_service_name" {
  type        = string
  description = "ADLS Gen2 linked service name"
}

variable "dataflow_name" {
  type        = string
  description = "Data flow name (if null, uses dataflow_name_prefix + random suffix)"
  default     = null
}

variable "dataflow_name_prefix" {
  type        = string
  description = "Prefix used to build the data flow name when dataflow_name is null"
  default     = "df-mlops-cancer-silver-gold"
}

variable "silver_source_dataset_name" {
  type        = string
  description = "Source dataset name (if null, uses silver_source_dataset_name_prefix + random suffix)"
  default     = null
}

variable "silver_source_dataset_name_prefix" {
  type        = string
  description = "Prefix used to build the source dataset name when silver_source_dataset_name is null"
  default     = "ds_silver_mlopscancer"
}

variable "source_container" {
  type        = string
  description = "ADLS container for the silver dataset"
  default     = "silver"
}

variable "source_folder" {
  type        = string
  description = "Folder path for the silver dataset"
  default     = "breast_cancer/clean"
}

variable "sink_container" {
  type        = string
  description = "ADLS container for the gold dataset"
  default     = "gold"
}

variable "sink_folder" {
  type        = string
  description = "Folder path for the gold dataset"
  default     = "breast_cancer/features"
}

variable "sink_format" {
  type        = string
  description = "Sink format (parquet or delimited)"
  default     = "parquet"
}
