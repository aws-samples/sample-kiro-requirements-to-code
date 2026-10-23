terraform {
  required_version = ">= 1.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Credentials come from the environment (CI role, SSO profile, instance role).
# Never hardcode them here. Region is a variable so the same configuration can
# be applied to any region via a tfvars file.
provider "aws" {
  region = var.aws_region
}
