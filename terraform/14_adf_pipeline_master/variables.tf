variable "data_factory_id" {
  type        = string
  description = "Data Factory ID that owns the pipeline"
}

variable "pipeline_name" {
  type        = string
  description = "Master pipeline name (if null, uses pipeline_name_prefix + random suffix)"
  default     = null
}

variable "pipeline_name_prefix" {
  type        = string
  description = "Prefix used to build the master pipeline name when pipeline_name is null"
  default     = "pl-mlops-cancer-master"
}

variable "ingest_pipeline_name" {
  type        = string
  description = "Pipeline name for HTTP ingest to bronze"
}

variable "silver_pipeline_name" {
  type        = string
  description = "Pipeline name for bronze -> silver dataflow"
}

variable "gold_pipeline_name" {
  type        = string
  description = "Pipeline name for silver -> gold dataflow"
}
