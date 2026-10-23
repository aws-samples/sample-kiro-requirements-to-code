terraform {
  # Partial backend configuration. The bucket and KMS key are created by
  # infra/bootstrap — replace the account ID below with your own, or pass the
  # values at init time:
  #
  #   terraform init \
  #     -backend-config="bucket=$(terraform -chdir=../bootstrap output -raw state_bucket_name)" \
  #     -backend-config="key=dev/terraform.tfstate"
  #
  backend "s3" {
    bucket     = "taskflow-dev-tfstate-111122223333"
    key        = "dev/terraform.tfstate"
    region     = "us-east-1"
    encrypt    = true
    kms_key_id = "alias/taskflow-dev-tfstate"

    # Native S3 state locking (Terraform 1.14+, DEC-101). No DynamoDB lock
    # table exists or is needed.
    use_lockfile = true
  }
}
