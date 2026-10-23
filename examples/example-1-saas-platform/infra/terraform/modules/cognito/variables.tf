variable "name_prefix" {
  description = "Prefix for all resource names, e.g. taskflow-dev. Also used as the hosted UI domain prefix, so it must be DNS-safe."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,40}[a-z0-9]$", var.name_prefix))
    error_message = "name_prefix must be lowercase alphanumeric with hyphens, start with a letter, end with a letter or digit, and be 3-42 characters."
  }
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod). Drives deletion protection."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod."
  }
}

variable "callback_urls" {
  description = "Allowed OAuth2 redirect URIs for the app client. HTTPS only, except http://localhost for local development."
  type        = list(string)

  validation {
    condition     = length(var.callback_urls) > 0
    error_message = "At least one callback URL is required."
  }

  validation {
    condition     = alltrue([for url in var.callback_urls : startswith(url, "https://") || startswith(url, "http://localhost")])
    error_message = "Callback URLs must use https://, or http://localhost for local development."
  }
}

variable "logout_urls" {
  description = "Allowed sign-out redirect URIs for the app client. Same scheme rules as callback_urls."
  type        = list(string)

  validation {
    condition     = length(var.logout_urls) > 0
    error_message = "At least one logout URL is required."
  }

  validation {
    condition     = alltrue([for url in var.logout_urls : startswith(url, "https://") || startswith(url, "http://localhost")])
    error_message = "Logout URLs must use https://, or http://localhost for local development."
  }
}

variable "password_min_length" {
  description = "Minimum password length enforced by the user pool password policy."
  type        = number
  default     = 12

  validation {
    condition     = var.password_min_length >= 8 && var.password_min_length <= 99
    error_message = "password_min_length must be between 8 and 99."
  }
}

variable "tags" {
  description = "Tags applied to every taggable resource in this module, merged with a per-resource Name tag."
  type        = map(string)
  default     = {}
}
