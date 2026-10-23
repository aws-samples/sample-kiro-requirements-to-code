# ---------------------------------------------------------------------------
# Foundation (story I1)
# ---------------------------------------------------------------------------

variable "project_name" {
  description = "Project name used as the first segment of every resource name."
  type        = string
  default     = "taskflow"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.project_name))
    error_message = "project_name must be lowercase alphanumeric with hyphens, 2-31 characters, starting with a letter."
  }
}

variable "environment" {
  description = "Deployment environment. Set per environment via environments/<env>.tfvars."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "aws_region" {
  description = "AWS region for all resources in this composition."
  type        = string
  default     = "us-east-1"

  validation {
    condition     = can(regex("^[a-z]{2}-[a-z]+-[0-9]$", var.aws_region))
    error_message = "aws_region must be a valid AWS region identifier, for example us-east-1."
  }
}

variable "extra_tags" {
  description = "Additional tags merged into common_tags and applied to every taggable resource."
  type        = map(string)
  default     = {}
}

# ---------------------------------------------------------------------------
# Authentication (story A1)
# ---------------------------------------------------------------------------

variable "callback_urls" {
  description = "Allowed OAuth2 redirect URIs for the Cognito app client. HTTPS only, except http://localhost for local development."
  type        = list(string)

  validation {
    condition     = length(var.callback_urls) > 0
    error_message = "At least one callback URL is required."
  }
}

variable "logout_urls" {
  description = "Allowed sign-out redirect URIs for the Cognito app client."
  type        = list(string)

  validation {
    condition     = length(var.logout_urls) > 0
    error_message = "At least one logout URL is required."
  }
}

variable "password_min_length" {
  description = "Minimum password length enforced by the Cognito password policy."
  type        = number
  default     = 12

  validation {
    condition     = var.password_min_length >= 8 && var.password_min_length <= 99
    error_message = "password_min_length must be between 8 and 99."
  }
}
