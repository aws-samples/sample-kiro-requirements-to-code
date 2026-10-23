terraform {
  # Remote state in S3 with native S3 locking (use_lockfile). No DynamoDB table.
  #
  # Partial configuration: the bucket, region and KMS key differ per account, so
  # they are supplied at init time and never committed here. For example:
  #
  #   terraform init \
  #     -backend-config="bucket=streamprocess-dev-tfstate-<account-id>" \
  #     -backend-config="region=us-east-1" \
  #     -backend-config="kms_key_id=arn:aws:kms:us-east-1:<account-id>:key/<key-id>"
  #
  # Local development and CI validation run with -backend=false.
  backend "s3" {
    key          = "streamprocess/101-rest-api-ingestion/terraform.tfstate"
    encrypt      = true
    use_lockfile = true
  }
}
