aws_region   = "us-east-1"
project_name = "streamprocess"
environment  = "dev"

api_stage_name           = "v1"
api_throttle_rate_limit  = 50
api_throttle_burst_limit = 100
api_quota_limit          = 100000
api_quota_period         = "MONTH"

lambda_memory_size     = 256
lambda_timeout_seconds = 30
lambda_architecture    = "arm64"

log_level          = "INFO"
log_retention_days = 14

# Dev accepts AWS managed encryption. Staging and prod pass a customer managed
# key ARN here, per the security baseline.
kms_key_arn = null

additional_tags = {
  CostCenter = "data-platform"
  Owner      = "data-platform-team"
}
