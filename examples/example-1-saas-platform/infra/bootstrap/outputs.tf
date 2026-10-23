output "state_bucket_name" {
  description = "Name of the S3 bucket holding Terraform remote state. Copy into infra/terraform/backend.tf."
  value       = aws_s3_bucket.state.id
}

output "kms_key_arn" {
  description = "ARN of the customer-managed KMS key encrypting the state bucket."
  value       = aws_kms_key.state.arn
}
