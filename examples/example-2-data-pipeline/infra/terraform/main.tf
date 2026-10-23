provider "aws" {
  region = var.aws_region
}

# Feature 101 — REST API ingestion. Story E4 owns this wiring; the Lambda source
# it packages comes from story E1.
module "ingestion" {
  source = "./modules/ingestion"

  name_prefix = local.name_prefix
  environment = var.environment
  tags        = local.common_tags

  lambda_source_dir      = local.lambda_source_dir
  layer_source_dir       = local.layer_source_dir
  lambda_memory_size     = var.lambda_memory_size
  lambda_timeout_seconds = var.lambda_timeout_seconds
  lambda_architecture    = var.lambda_architecture
  log_level              = var.log_level
  log_retention_days     = var.log_retention_days

  api_stage_name           = var.api_stage_name
  api_throttle_rate_limit  = var.api_throttle_rate_limit
  api_throttle_burst_limit = var.api_throttle_burst_limit
  api_quota_limit          = var.api_quota_limit
  api_quota_period         = var.api_quota_period

  dlq_retention_seconds = var.dlq_retention_seconds
  kms_key_arn           = var.kms_key_arn
}
