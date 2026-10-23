terraform {
  required_version = ">= 1.14"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # No backend block on purpose. Bootstrap runs once with local state because
  # it creates the very bucket the other configurations use as a backend.
  # See README.md in this directory.
}

provider "aws" {
  region = var.aws_region
}
