variable "name_prefix" {
  type        = string
  description = "Prefix applied to every resource name, e.g. streamprocess-dev."
}

variable "environment" {
  type        = string
  description = "Deployment environment, published to the function as ENVIRONMENT."
}

variable "tags" {
  type        = map(string)
  description = "Common tags applied to every taggable resource in the module."
}

variable "lambda_source_dir" {
  type        = string
  description = "Directory zipped into the function package. Its contents become the package root, so the ingest package must sit directly inside it."
}

variable "layer_source_dir" {
  type        = string
  description = "Directory zipped into the shared layer. Must contain a python/ subdirectory so the modules land on /opt/python."
}

variable "lambda_handler" {
  type        = string
  description = "Entry point for the ingestion function, as package.module.function."
  default     = "ingest.handler.handler"
}

variable "lambda_runtime" {
  type        = string
  description = "Lambda runtime identifier. Python 3.12 is mandated by the technology guidelines."
  default     = "python3.12"
}

variable "lambda_architecture" {
  type        = string
  description = "Instruction set for the function and the layer. Compiled dependencies must match it."
  default     = "arm64"
}

variable "lambda_memory_size" {
  type        = number
  description = "Memory in MB allocated to the ingestion Lambda."
  default     = 256
}

variable "lambda_timeout_seconds" {
  type        = number
  description = "Timeout in seconds for the ingestion Lambda."
  default     = 30
}

variable "log_level" {
  type        = string
  description = "Powertools log level published to the function as LOG_LEVEL."
  default     = "INFO"
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch Logs retention in days for the function log group."
  default     = 14
}

variable "api_stage_name" {
  type        = string
  description = "API Gateway stage name, which becomes the first path segment of the invoke URL."
  default     = "v1"
}

variable "api_throttle_rate_limit" {
  type        = number
  description = "Steady-state requests per second allowed per API key."
  default     = 50
}

variable "api_throttle_burst_limit" {
  type        = number
  description = "Burst capacity in requests allowed per API key."
  default     = 100
}

variable "api_quota_limit" {
  type        = number
  description = "Maximum number of requests an API key may make per quota period."
  default     = 100000
}

variable "api_quota_period" {
  type        = string
  description = "Quota period for the usage plan: DAY, WEEK or MONTH."
  default     = "MONTH"
}

variable "dlq_retention_seconds" {
  type        = number
  description = "Retention in seconds for the dead-letter queue."
  default     = 1209600
}

variable "kms_key_arn" {
  type        = string
  description = "Customer managed KMS key ARN for the DLQ and the log group. When null, AWS managed encryption is used instead."
  default     = null
}
