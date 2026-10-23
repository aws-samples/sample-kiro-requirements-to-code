locals {
  # Every resource name starts with this prefix, e.g. streamprocess-dev-ingest-api.
  name_prefix = "${var.project_name}-${var.environment}"

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Feature     = "101-rest-api-ingestion"
      Repository  = "aws-samples-reference/examples/example-2-data-pipeline"
    },
    var.additional_tags,
  )

  # Repository root, resolved from the configuration directory so the defaults
  # work no matter where terraform is invoked from.
  source_root = abspath("${path.root}/../..")

  lambda_source_dir = coalesce(var.lambda_source_dir, "${local.source_root}/src/functions")
  layer_source_dir  = coalesce(var.layer_source_dir, "${local.source_root}/src/layers/common")
}
