variable "aws_region" {
  type        = string
  description = "AWS region the ingestion stack is deployed into."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Project slug used as the first segment of every resource name."
  default     = "streamprocess"
}

variable "environment" {
  type        = string
  description = "Deployment environment. Drives naming, tagging and log retention."

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "api_stage_name" {
  type        = string
  description = "API Gateway stage name, which becomes the first path segment of the invoke URL."
  default     = "v1"
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch Logs retention for the ingestion Lambda. 14 in dev, 90 in prod."
  default     = 14

  validation {
    condition     = contains([1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653], var.log_retention_days)
    error_message = "log_retention_days must be a retention period supported by CloudWatch Logs."
  }
}

variable "log_level" {
  type        = string
  description = "Powertools log level for the ingestion Lambda."
  default     = "INFO"

  validation {
    condition     = contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.log_level)
    error_message = "log_level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL."
  }
}

variable "lambda_memory_size" {
  type        = number
  description = "Memory in MB for the ingestion Lambda. Start at 256 and right-size from metrics."
  default     = 256

  validation {
    condition     = var.lambda_memory_size >= 128 && var.lambda_memory_size <= 10240
    error_message = "lambda_memory_size must be between 128 and 10240 MB."
  }
}

variable "lambda_timeout_seconds" {
  type        = number
  description = "Timeout in seconds for the ingestion Lambda. Capped at 60 by the technology guidelines."
  default     = 30

  validation {
    condition     = var.lambda_timeout_seconds > 0 && var.lambda_timeout_seconds <= 60
    error_message = "lambda_timeout_seconds must be between 1 and 60 seconds."
  }
}

variable "lambda_architecture" {
  type        = string
  description = "Instruction set for the ingestion Lambda. Compiled dependencies must match it."
  default     = "arm64"

  validation {
    condition     = contains(["arm64", "x86_64"], var.lambda_architecture)
    error_message = "lambda_architecture must be arm64 or x86_64."
  }
}

variable "lambda_source_dir" {
  type        = string
  description = "Directory zipped into the function package. Defaults to src/functions in this repository; CI overrides it with the build output that also contains the pip dependencies."
  default     = null
}

variable "layer_source_dir" {
  type        = string
  description = "Directory zipped into the shared layer. Must contain a python/ subdirectory. Defaults to src/layers/common in this repository."
  default     = null
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
  description = "Quota period for the usage plan."
  default     = "MONTH"

  validation {
    condition     = contains(["DAY", "WEEK", "MONTH"], var.api_quota_period)
    error_message = "api_quota_period must be one of: DAY, WEEK, MONTH."
  }
}

variable "dlq_retention_seconds" {
  type        = number
  description = "Retention for the ingestion dead-letter queue. 14 days per the infrastructure guidelines."
  default     = 1209600
}

variable "kms_key_arn" {
  type        = string
  description = "Customer managed KMS key ARN used to encrypt the DLQ and the log group. When null, AWS managed encryption is used, which is acceptable in dev only."
  default     = null
}

variable "additional_tags" {
  type        = map(string)
  description = "Extra tags merged into the common tag set applied to every resource."
  default     = {}
}
