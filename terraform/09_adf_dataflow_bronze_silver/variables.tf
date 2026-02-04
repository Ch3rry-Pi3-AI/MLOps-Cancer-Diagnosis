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
  default     = "df-mlops-cancer-bronze-silver"
}

variable "bronze_source_dataset_name" {
  type        = string
  description = "Source dataset name (if null, uses bronze_source_dataset_name_prefix + random suffix)"
  default     = null
}

variable "bronze_source_dataset_name_prefix" {
  type        = string
  description = "Prefix used to build the source dataset name when bronze_source_dataset_name is null"
  default     = "ds_bronze_mlopscancer"
}

variable "source_container" {
  type        = string
  description = "ADLS container for the bronze dataset"
  default     = "bronze"
}

variable "source_folder" {
  type        = string
  description = "Folder path for the bronze dataset"
  default     = "breast_cancer/raw"
}

variable "source_file" {
  type        = string
  description = "File name for the bronze dataset"
  default     = "breast_cancer.csv"
}

variable "sink_container" {
  type        = string
  description = "ADLS container for the silver dataset"
  default     = "silver"
}

variable "sink_folder" {
  type        = string
  description = "Folder path for the silver dataset"
  default     = "breast_cancer/clean"
}

variable "sink_format" {
  type        = string
  description = "Sink format (parquet or delimited)"
  default     = "parquet"
}
