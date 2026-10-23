---
trackerId: ADO-12314
ref: I4
parent: 301
title: "Aurora Serverless v2, attachment S3 buckets and KMS keys"
state: New
sprint: S2
owner: bob
effort: 3
priority: 1
tags: [infra, terraform, database, PI1]
dependsOn: [I2]
lastSync: 2026-07-18T09:42:00Z
---

## Context

Fourth and final infrastructure story in Feature 301, covering requirement R4. Implements DEC-103 (Aurora PostgreSQL Serverless v2) and provisions the encrypted storage layer: the database, the file attachment bucket, and the customer-managed KMS keys both depend on. Scheduled for Sprint 2 because the cluster is placed in the private subnets from I2.

## Goal

As a platform engineer, I want an auto-scaling PostgreSQL cluster and an encrypted attachment bucket so that the API has a multi-tenant data store and file storage without any capacity planning.

## Scope

- New Terraform module at `infra/terraform/modules/aurora/` and `infra/terraform/modules/s3/`, both following the module conventions (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`)
- Aurora PostgreSQL Serverless v2 cluster, engine version 16, `serverlessv2_scaling_configuration` from 0.5 to 16 ACU
- Writer instance plus a Multi-AZ reader instance, so failover has a target
- DB subnet group across the private subnets from I2, database security group from I2 attached
- Master credentials managed by RDS in Secrets Manager (`manage_master_user_password`) so no password ever enters `.tf`, `.tfvars` or state
- Schema-per-tenant readiness: a single logical database, `search_path` left to the application, and a DB parameter group with `max_connections` and statement timeout tuned for connection pooling — no tenant identifier is hardcoded anywhere in the module
- Automated backups with configurable retention, `deletion_protection` on, `storage_encrypted` with the data CMK, Performance Insights and CloudWatch log exports for `postgresql`
- S3 attachment bucket: versioning enabled, SSE-KMS with the attachment CMK and bucket keys enabled, public access fully blocked, TLS-only bucket policy, lifecycle rules transitioning noncurrent versions to IA then expiring them
- Separate customer-managed KMS keys per data category (database, attachments) with rotation enabled, aliases, and key policies granting only the roles that need them
- Outputs: cluster endpoints, reader endpoint, port, database name, master secret ARN, bucket name/ARN, KMS key ARNs and alias names
- Wire both modules into the root composition and `environments/dev.tfvars`

## Out of Scope

- Database schema, tables and Alembic migrations — owned by the application data-layer stories
- Tenant provisioning automation (creating a schema per new tenant at signup)
- Aurora Global Database and cross-region replication — part of multi-region DR, deferred to PI 3
- RDS Proxy — revisit if ECS task connection counts become a problem
- CloudFront distribution in front of the attachment bucket — deferred to PI 2
- Cross-account bucket replication and Object Lock

## Dependencies

- Requires: I2 (VPC module provides the private subnet IDs for the DB subnet group and the database security group)
- Blocks: API data-layer stories in Epic 2, which need the cluster endpoint and the master secret ARN; attachment upload stories, which need the bucket name and CMK

## Acceptance Criteria

- **Given** the modules at `infra/terraform/modules/aurora/` and `infra/terraform/modules/s3/`, **When** I run `terraform validate` and `terraform plan -var-file=environments/dev.tfvars`, **Then** the plan succeeds and shows an Aurora cluster, two cluster instances, a DB subnet group, a parameter group, an S3 bucket and two KMS keys.
- **Given** the cluster configuration, **When** I inspect its engine settings, **Then** `engine_mode` is provisioned with `engine = "aurora-postgresql"`, engine version 16, and a `serverlessv2_scaling_configuration` of `min_capacity = 0.5` and `max_capacity = 16`.
- **Given** the cluster instances, **When** I inspect their placement, **Then** the writer and the reader are in different availability zones drawn from the private subnets supplied by I2.
- **Given** the cluster is provisioned, **When** I search the Terraform configuration and state for a master password, **Then** none exists, because RDS manages the credential in Secrets Manager and the module only outputs the secret ARN.
- **Given** the database security group from I2, **When** I attempt to connect from outside the VPC, **Then** the connection is refused because the cluster is not publicly accessible and only the ECS task security group may reach port 5432.
- **Given** `storage_encrypted` and the database CMK, **When** I inspect the cluster, **Then** encryption at rest uses the customer-managed key rather than the AWS managed `aws/rds` key.
- **Given** the multi-tenant model, **When** I grep the module for tenant identifiers, **Then** none are hardcoded and tenant-specific configuration is driven from variables.
- **Given** the attachment bucket, **When** I inspect its configuration, **Then** versioning is enabled, default encryption is SSE-KMS with the attachment CMK, bucket keys are enabled, and all four public access block settings are `true`.
- **Given** the bucket policy, **When** a request arrives over plain HTTP, **Then** it is denied by the `aws:SecureTransport` condition.
- **Given** the lifecycle configuration, **When** an object version becomes noncurrent, **Then** it transitions to Standard-IA after 30 days and expires after the configured retention.
- **Given** the two KMS keys, **When** I inspect them, **Then** each has automatic rotation enabled, a distinct alias, and a key policy that names only the roles requiring access rather than granting to the whole account.
- **Given** the module outputs, **When** consumed by the root composition, **Then** `cluster_endpoint`, `cluster_reader_endpoint`, `cluster_port`, `database_name`, `master_secret_arn`, `attachments_bucket_name`, `attachments_bucket_arn`, `database_kms_key_arn` and `attachments_kms_key_arn` are available, with the secret ARN marked sensitive.
- **Given** a change to either module, **When** pre-commit and CI run, **Then** `terraform fmt`, `terraform validate`, `tflint` and `checkov` all pass with no high-severity findings.
