---
trackerId: ADO-12301
ref: A1
parent: 101
title: "Cognito User Pool Terraform Module — user pool, app client, custom attributes"
state: Done
sprint: S1
owner: alice
effort: 4
priority: 2
tags: [auth, infra, terraform, PI1]
dependsOn: []
lastSync: 2026-07-18T09:42:00Z
---

## Context

First story in Feature 101 (Authentication & Authorization). Provisions the AWS Cognito infrastructure that all authentication flows depend on. Must be deployed before the JWT middleware (A2) can validate tokens.

## Goal

As a platform engineer, I want a Terraform module for AWS Cognito so that the team has a managed identity provider with tenant-aware custom attributes, ready for application integration.

## Scope

- Cognito User Pool with password policy and MFA-ready config
- Custom attributes: `tenant_id` (immutable), `role` (mutable)
- App client with OAuth2 Authorization Code + PKCE flow
- Callback URLs configurable per environment
- User pool domain for hosted UI (temporary, until custom UI in PI 2)
- Terraform module following project conventions (name_prefix, tags, outputs)
- README with usage example

## Out of Scope

- Custom UI for login/signup (PI 2)
- Social identity providers (PI 2)
- MFA enforcement (infrastructure ready, enforcement in PI 2)
- Tenant provisioning automation (separate story)

## Dependencies

- Requires: Terraform foundation (infra/terraform/ exists with state backend)
- Blocks: A2 (JWT Middleware needs user pool ID and JWKS URL)

## Acceptance Criteria

- **Given** the Terraform module at `infra/terraform/modules/cognito/`, **When** I run `terraform plan`, **Then** it creates a User Pool, App Client, and User Pool Domain with no errors.
- **Given** the User Pool is provisioned, **When** I inspect custom attributes, **Then** `custom:tenant_id` (string, immutable) and `custom:role` (string, mutable) exist.
- **Given** the App Client configuration, **When** I check OAuth2 settings, **Then** Authorization Code grant with PKCE is enabled, implicit grant is disabled.
- **Given** `var.callback_urls` is set to `["http://localhost:3000/callback"]`, **When** the App Client is created, **Then** those URLs are registered as allowed callbacks.
- **Given** the module outputs, **When** consumed by the root composition, **Then** `user_pool_id`, `user_pool_arn`, `app_client_id`, `jwks_url`, and `user_pool_domain` are available.
- **Given** the module README, **When** a new engineer reads it, **Then** they can understand inputs, outputs, and usage within 5 minutes.

## Implementation Tasks

### Task 1: Create Cognito Terraform Module

- [x] 1.1 Create `infra/terraform/modules/cognito/versions.tf` — pin terraform >= 1.14, aws ~> 5.0
- [x] 1.2 Create `infra/terraform/modules/cognito/variables.tf` — inputs: `name_prefix`, `environment`, `callback_urls`, `logout_urls`, `password_min_length` (default 12), `tags`
- [x] 1.3 Create `infra/terraform/modules/cognito/main.tf`:
  - `aws_cognito_user_pool` — password policy, account recovery, custom attributes (tenant_id immutable, role mutable), schema validation
  - `aws_cognito_user_pool_client` — PKCE flow, token validity, read/write attributes, explicit auth flows
  - `aws_cognito_user_pool_domain` — prefix-based domain using name_prefix
- [x] 1.4 Create `infra/terraform/modules/cognito/outputs.tf` — user_pool_id, user_pool_arn, app_client_id, app_client_secret (sensitive), jwks_url (constructed), user_pool_domain, user_pool_endpoint
- [x] 1.5 Create `infra/terraform/modules/cognito/README.md` — module description, usage example, inputs table, outputs table

### Task 2: Wire Module into Root Composition

- [x] 2.1 Add `module "cognito"` block to `infra/terraform/main.tf` referencing the module
- [x] 2.2 Add Cognito-specific variables to root `variables.tf` (callback_urls, password policy)
- [x] 2.3 Add Cognito outputs to root `outputs.tf`
- [x] 2.4 Update `environments/dev.tfvars` with dev callback URLs

### Task 3: Validation

- [x] 3.1 `terraform fmt -check -recursive` — passes
- [x] 3.2 `terraform validate` — passes
- [x] 3.3 `tflint` on cognito module — no findings
- [x] 3.4 `checkov` — no high-severity findings
- [x] 3.5 `terraform plan -var-file=environments/dev.tfvars` — shows expected Cognito resources
- [x] 3.6 Manual review: verify custom attributes are immutable/mutable as specified
