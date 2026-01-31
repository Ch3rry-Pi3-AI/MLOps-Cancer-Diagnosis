variable "workspace_id" {
  type        = string
  description = "AML workspace ID for the compute cluster"
}

variable "location" {
  type        = string
  description = "Azure region for the compute cluster"
}

variable "compute_name" {
  type        = string
  description = "Compute cluster name"
  default     = "cpu-cluster"
}

variable "vm_size" {
  type        = string
  description = "VM size for the cluster"
  default     = "Standard_DS3_v2"
}

variable "vm_priority" {
  type        = string
  description = "VM priority (Dedicated or LowPriority)"
  default     = "Dedicated"
}

variable "min_instances" {
  type        = number
  description = "Minimum number of nodes"
  default     = 0
}

variable "max_instances" {
  type        = number
  description = "Maximum number of nodes"
  default     = 2
}

variable "idle_time_before_scaledown" {
  type        = string
  description = "Idle time before scale down (ISO 8601 duration, e.g. PT2M)"
  default     = "PT2M"
}

variable "tags" {
  type        = map(string)
  description = "Tags applied to the compute"
  default     = {}
}
