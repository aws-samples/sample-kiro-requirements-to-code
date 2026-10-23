# ADR 0002 — S3 native locking for Terraform state

**Status:** Accepted
**Date:** 2026-07-14
**Story:** I1 (Terraform Foundation, Feature 301)
**Design decision:** DEC-101 in `.kiro/specs/301-terraform-foundation/design.md`

## Context

Feature 301 needs a remote state backend that supports concurrent team access with
safe locking. Terraform offers three practical options for AWS-hosted state: S3 with
a DynamoDB lock table (the legacy approach), S3 with native locking (Terraform 1.14+),
and Terraform Cloud. The `infra/bootstrap/` folder provisions the state bucket and KMS
key; this decision records why it is S3-native rather than either alternative.

The project `versions.tf` already requires `terraform >= 1.14`, which is the minimum
version for S3 native locking, so the version constraint and this decision are
consistent without any additional floor.

## Decision

Use **S3 + `use_lockfile = true`** (Terraform 1.14+ native locking).

`backend.tf` sets:

```hcl
backend "s3" {
  encrypt      = true
  use_lockfile = true
  # bucket, region, key supplied at init time via -backend-config
  # so no account-specific values are committed to the repository
}
```

No DynamoDB lock table is created or referenced.

## Alternatives Considered

| Option | Reason rejected |
|--------|----------------|
| S3 + DynamoDB lock table | Extra resource to provision, monitor, and pay for; native locking makes it redundant on Terraform 1.14+ |
| Terraform Cloud | Additional vendor dependency; cost at team scale; network egress for state reads during every plan/apply |
| Local state | Not viable for team collaboration — state diverges as soon as two engineers run `terraform apply` |

## Consequences

- Simpler infrastructure: no DynamoDB table in `infra/bootstrap/main.tf`, one fewer
  IAM statement in the plan role (no `dynamodb:*`), and no lock-table ARN to thread
  through outputs.
- Hard floor: any environment whose backend config does not supply
  `use_lockfile = true` falls back to no locking rather than failing loudly.
  The `backend.tf` in this repo sets it explicitly; do not remove it.
- State file is a partial configuration: `bucket`, `region`, and `kms_key_id` are
  passed via `-backend-config` at `terraform init` time, keeping account-specific
  values out of version control. CI workflows supply these from repository variables
  (`vars.TF_STATE_BUCKET`, `vars.AWS_REGION`). See `.github/workflows/terraform-plan.yml`.

## Rollback Path

If native locking proves unreliable (e.g., object-lock contention under aggressive
concurrent plans), add a DynamoDB table to `infra/bootstrap/main.tf`, add
`dynamodb_table` to `backend.tf`, and add `dynamodb:GetItem`, `dynamodb:PutItem`,
`dynamodb:DeleteItem` to the plan role policy. No state migration is required —
adding a lock table does not change the state file format.
