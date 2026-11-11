# Terraform Bootstrap

Creates the remote state backend for TaskFlow: a versioned, KMS-encrypted S3
bucket with public access blocked.

This configuration is a chicken-and-egg exception. It runs **once per AWS
account, with local state**, because it creates the bucket that every other
configuration uses as its backend. Everything else in `infra/` uses the S3
backend with native locking (`use_lockfile = true`, see DEC-101 in
`.kiro/specs/301-terraform-foundation/design.md`) — no DynamoDB lock table.

## What it creates

| Resource | Purpose |
|----------|---------|
| `aws_kms_key` + alias | Customer-managed CMK, yearly rotation enabled, explicit key policy (account root admin + S3 service use scoped to this account and bucket) |
| `aws_s3_bucket` | State bucket, `prevent_destroy` lifecycle guard |
| `aws_s3_bucket_versioning` | Recover a corrupted or truncated state file |
| `aws_s3_bucket_server_side_encryption_configuration` | SSE-KMS with the CMK above, bucket keys on |
| `aws_s3_bucket_public_access_block` | All four public-access blocks on |
| `aws_s3_bucket_ownership_controls` | `BucketOwnerEnforced` (ACLs disabled) |
| `aws_s3_bucket_policy` | Denies any request where `aws:SecureTransport` is false |

The bucket is named `<project>-<environment>-tfstate-<account-id>`. The account
ID suffix keeps the name globally unique without a random suffix, so the name is
reproducible.

## Usage

Run from this directory with credentials for the target account:

```bash
terraform init                      # local state, no backend
terraform plan  -out=bootstrap.plan
terraform apply bootstrap.plan
```

Override the defaults (`taskflow` / `dev` / `us-east-1`) if needed:

```bash
terraform apply -var="environment=staging" -var="aws_region=eu-west-1"
```

Then copy the outputs into the root configuration's backend:

```bash
terraform output -raw state_bucket_name
terraform output -raw kms_key_arn
```

Set `bucket` and `kms_key_id` in `../terraform/backend.tf`, then initialize the
root configuration:

```bash
cd ../terraform
terraform init -backend-config="key=dev/terraform.tfstate"
```

## Notes

- Commit the local `terraform.tfstate` produced here **only if** your team has
  agreed to it. It contains no secrets, but the usual practice is to treat this
  configuration as run-once and re-import if it ever needs changing.
- `prevent_destroy` is set on the bucket. `terraform destroy` will fail by
  design; removing the state backend is a deliberate, manual operation.
- The KMS key has a 30-day deletion window. Scheduling its deletion makes every
  existing state file unreadable.
