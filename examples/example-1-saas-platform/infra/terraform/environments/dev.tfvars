# Development environment.
#
#   terraform plan -var-file=environments/dev.tfvars
#
# No secrets here. Anything sensitive comes from Secrets Manager or SSM via a
# data source.

project_name = "taskflow"
environment  = "dev"
aws_region   = "us-east-1"

extra_tags = {
  Owner      = "platform-team"
  CostCenter = "engineering"
}

# Authentication (story A1) — local dev runs the frontend on localhost:3000.
callback_urls = ["http://localhost:3000/callback"]
logout_urls   = ["http://localhost:3000/logout"]

password_min_length = 12
