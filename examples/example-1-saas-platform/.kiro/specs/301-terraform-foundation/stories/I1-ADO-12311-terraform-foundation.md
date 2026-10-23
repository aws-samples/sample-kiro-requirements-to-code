---
trackerId: ADO-12311
ref: I1
parent: 301
title: "Terraform foundation — remote state, module layout, pre-commit quality gates"
state: Done
sprint: S1
owner: alice
effort: 3
priority: 1
tags: [infra, terraform, devops, PI1]
dependsOn: []
lastSync: 2026-07-14T11:00:00Z
---

## Context

First infrastructure story. Establishes the Terraform conventions, remote state, and local quality gates that every subsequent infra story builds upon. No AWS resources beyond the state bucket are created here. The CI/CD pipeline that plans on PR and applies on merge is Feature 302, which adopts the workflows in `templates/workflows/` against this foundation.

## Goal

As a platform engineer, I want a well-organized Terraform foundation so that all infrastructure work follows consistent conventions and is validated before it ever reaches a pull request.

## Scope

- Bootstrap config (state S3 bucket + KMS key, run once with local state)
- Root composition structure (main.tf, variables.tf, outputs.tf, locals.tf, backend.tf, versions.tf)
- Module directory layout convention
- Environment-specific tfvars
- Pre-commit hooks (fmt, validate, tflint)
- README with usage, conventions, and directory map

## Out of Scope

- Any application-specific infrastructure (VPC, ECS, Aurora — those are I2-I4)
- CI/CD pipeline — plan on PR, apply on merge (Feature 302; workflow templates ready in `templates/workflows/`)
- Production environment config (dev only for now)
- Checkov security scanning (added in Sprint 2 when there are real resources)

## Dependencies

- None (this is the foundation)
- Blocks: I2, I3, I4, and all other infra stories; Feature 302 (CI/CD) builds on this state backend

## Acceptance Criteria

- **Given** a clean clone of the repo, **When** I run `terraform init -backend-config="key=dev/terraform.tfstate"`, **Then** it initializes against the S3 remote state with native locking.
- **Given** the bootstrap stack has been applied once, **When** I read its outputs, **Then** `state_bucket_name` and `kms_key_arn` are available for backend configuration.
- **Given** a change to any `.tf` file, **When** I commit, **Then** pre-commit runs `terraform fmt` and `tflint` and blocks on failure.
- **Given** the README at `infra/terraform/README.md`, **When** a new engineer reads it, **Then** they understand the directory structure, conventions, and how to add a new module.

## Implementation Tasks

### Task 1: Bootstrap Configuration

- [x] 1.1 Create `infra/bootstrap/versions.tf` — terraform >= 1.14, aws ~> 5.0
- [x] 1.2 Create `infra/bootstrap/variables.tf` — project_name, environment, aws_region
- [x] 1.3 Create `infra/bootstrap/main.tf` — S3 bucket (versioning, KMS, block public access), KMS key
- [x] 1.4 Create `infra/bootstrap/outputs.tf` — state_bucket_name, kms_key_arn
- [x] 1.5 Create `infra/bootstrap/README.md` — usage instructions

### Task 2: Root Composition

- [x] 2.1 Create `infra/terraform/versions.tf` — terraform >= 1.14, aws ~> 5.0
- [x] 2.2 Create `infra/terraform/backend.tf` — S3 backend, use_lockfile = true
- [x] 2.3 Create `infra/terraform/variables.tf` — project_name, environment, aws_region, extra_tags
- [x] 2.4 Create `infra/terraform/locals.tf` — name_prefix, common_tags
- [x] 2.5 Create `infra/terraform/main.tf` — placeholder module blocks
- [x] 2.6 Create `infra/terraform/outputs.tf` — placeholder structure
- [x] 2.7 Create `infra/terraform/environments/dev.tfvars`

### Task 3: Quality Gates

- [x] 3.1 Create `.pre-commit-config.yaml` — terraform fmt, validate, tflint
- [x] 3.2 Create `infra/terraform/.tflint.hcl` — AWS ruleset

### Task 4: Documentation

- [x] 4.1 Create `infra/terraform/README.md` — full usage guide

### Task 5: Validation

- [x] 5.1 `terraform fmt -check -recursive` — passes in both bootstrap and terraform dirs
- [x] 5.2 `terraform validate` — passes
- [x] 5.3 `tflint` — no findings
