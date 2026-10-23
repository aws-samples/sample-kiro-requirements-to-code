---
trackerId: pending
ref: E4
parent: 101
title: "Terraform ingestion module — API Gateway, Lambda, IAM, DLQ, log group"
state: Done
sprint: S1
owner: eric
effort: 2
priority: 1
tags: [ingestion, infra, terraform, PI1]
dependsOn: []
lastSync: 1970-01-01T00:00:00Z
---

## Context

Second story in Feature 101, covering requirement R4. Delivers the Terraform that provisions the whole ingestion stack described by DEC-001 (API Gateway REST with Lambda proxy integration): the REST API, the ingestion Lambda and its shared layer, a scoped execution role, a dead-letter queue and a log group. Sequenced in Sprint 1 alongside E1 so infrastructure exists before E2 and E3 extend it.

## Goal

As a platform engineer, I want the ingestion stack defined as a reusable Terraform module so that every environment is provisioned identically from version control, with no hand-created API Gateway or Lambda resources.

## Scope

- Root composition at `infra/terraform/` — `versions.tf`, `backend.tf`, `variables.tf`, `locals.tf`, `main.tf`, `outputs.tf` and `environments/dev.tfvars`
- Remote state on S3 with `use_lockfile = true` and no DynamoDB lock table, configured as a partial backend so bucket, region and KMS key are supplied at `init` time
- Reusable module at `infra/terraform/modules/ingestion/` following the mandated layout (`main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`)
- API Gateway REGIONAL REST API with `POST /events`, `AWS_PROXY` integration, a deployed stage with X-Ray tracing, per-method throttling, an API key and a usage plan carrying the quota
- Ingestion Lambda plus the shared `common` layer, both packaged with `archive_file`, running Python 3.12 on arm64 with X-Ray tracing active
- SQS dead-letter queue with 14-day retention, wired to the function's `dead_letter_config` and exported for story E2 to write to from inside the handler
- Least-privilege execution role: log writes scoped to the module's own log group, `sqs:SendMessage` scoped to the DLQ ARN, KMS grants added only when a customer-managed key is supplied
- CloudWatch log group at `/aws/lambda/streamprocess-dev-ingest-api` with configurable retention
- Optional customer-managed KMS key for the DLQ and log group, so dev can run on AWS managed encryption while staging and prod pass a CMK
- Module README documenting the packaging contract, inputs, outputs and known gaps

## Out of Scope

- The Lambda handler source itself — owned by story E1; this module only packages whatever is in the configured source directories
- Kinesis Data Stream and the IAM grants to write to it (E3)
- Schema bucket, DLQ alarm and schema management endpoints (E2)
- API Gateway request validators — Content-Type and empty-body checks return RFC 7807 from the handler per E1's acceptance criteria
- Account-level `aws_api_gateway_account.cloudwatch_role_arn`, which is global state this module deliberately does not own
- Provisioned concurrency — cold starts accepted in dev per design.md open question 1
- Staging and prod tfvars, WAF, and the CI/CD workflows

## Dependencies

- None — this story has no upstream story dependencies, matching `dependsOn: []`. The function and layer source directories are module inputs, so the configuration formats, validates and plans before story E1's handler code lands.
- Blocks: E1 (needs this module to deploy the handler beyond a manual dev deployment), E2 (consumes the dead-letter queue), E3 (extends this module with the Kinesis stream and its IAM grants)

## Acceptance Criteria

- **Given** a clean clone, **When** I run `terraform init -backend=false` followed by `terraform validate` in `infra/terraform/`, **Then** both succeed for the root composition and the ingestion module with no errors.
- **Given** `backend.tf`, **When** I inspect the state configuration, **Then** it declares the S3 backend with `encrypt = true` and `use_lockfile = true`, carries no DynamoDB lock table, and leaves bucket, region and KMS key to `-backend-config` at init time so no account-specific value is committed.
- **Given** `terraform plan -var-file=environments/dev.tfvars`, **When** the plan is generated, **Then** it creates the REST API, the `events` resource, the `POST` method, the `AWS_PROXY` integration, a deployment, a stage, method settings, an API key, a usage plan, a usage plan key, the Lambda function, the layer version, the log group, the IAM role and inline policy, the Lambda permission and the SQS dead-letter queue.
- **Given** the `POST /events` method, **When** I inspect its configuration, **Then** `authorization` is `NONE` and `api_key_required` is `true`, so requests without `x-api-key` are rejected by API Gateway before the function is invoked.
- **Given** the ingestion function, **When** I inspect it, **Then** the runtime is `python3.12`, the architecture is `arm64`, memory is 256 MB, timeout is 30 s, the shared layer is attached, `tracing_config` mode is `Active`, and `dead_letter_config.target_arn` points at the ingestion DLQ — satisfying the per-function requirements in `infra-guidelines.md`.
- **Given** the packaging contract, **When** the archives are built, **Then** the function zip is rooted at `lambda_source_dir` so the handler resolves as `ingest.handler.handler`, the layer zip is rooted at `layer_source_dir` so its `python/` directory lands on `/opt/python`, both archives exclude `__pycache__` and `*.pyc`, and the function archive additionally excludes `requirements.txt`.
- **Given** `infra-guidelines.md` requires a dead-letter queue for every Lambda, **When** the module applies, **Then** an SQS queue named `streamprocess-dev-ingest-dlq` exists with 14-day (1209600 s) retention and the execution role is granted `sqs:SendMessage` on that queue ARN and nothing else.
- **Given** the execution role policy, **When** I inspect its statements, **Then** log writes are scoped to the module's own log group ARN, `xray:PutTraceSegments` and `xray:PutTelemetryRecords` use `*` only because X-Ray segment ingestion has no resource-level permissions, and no other statement uses a wildcard resource.
- **Given** `kms_key_arn = null` in dev, **When** the plan is generated, **Then** the DLQ falls back to SQS managed SSE and no KMS statement is added to the role policy; **Given** a customer-managed key ARN, **When** the plan is generated, **Then** the DLQ and the log group are encrypted with it and the role gains `kms:Decrypt` and `kms:GenerateDataKey` scoped to that key alone.
- **Given** access and execution logging require an account-level API Gateway CloudWatch role that this module does not own, **When** method settings are applied, **Then** `logging_level` is `OFF` while `metrics_enabled` is `true`, `data_trace_enabled` is `false`, and per-method throttling is set from `api_throttle_rate_limit` and `api_throttle_burst_limit` — and the README records the gap and how to close it.
- **Given** the log group, **When** I inspect it, **Then** its name is `/aws/lambda/streamprocess-dev-ingest-api` with `retention_in_days` of 14 in dev.
- **Given** the Lambda permission, **When** I inspect its `source_arn`, **Then** invocation is restricted to the ingestion API's execution ARN for `POST /events` rather than the whole API.
- **Given** the usage plan, **When** I inspect it, **Then** it binds the API key to the deployed stage with a 50 rps steady rate, 100 burst, and a 100000-request `MONTH` quota, matching `dev.tfvars`.
- **Given** the outputs, **When** apply completes, **Then** `events_endpoint_url`, `api_id`, `api_key_id`, `usage_plan_id`, `lambda_function_name`, `lambda_function_arn`, `lambda_log_group_name`, `common_layer_arn` and `dead_letter_queue_url` are available at the root, and the API key *value* is never emitted as an output.
- **Given** the module README, **When** a new engineer reads it, **Then** they can find the resource inventory, a usage example, the CI packaging commands for arm64 wheels, the inputs and outputs tables, and the documented known gaps.
- **Given** any change under `infra/`, **When** the quality gates run, **Then** `terraform fmt -check -recursive`, `terraform validate` and `tflint` all pass with no findings.

## Implementation Tasks

### Task 1: Root Composition

- [x] 1.1 Create `infra/terraform/versions.tf` — pin `required_version >= 1.14` and `hashicorp/aws ~> 5.0`
- [x] 1.2 Create `infra/terraform/backend.tf` — S3 backend with `key = "streamprocess/101-rest-api-ingestion/terraform.tfstate"`, `encrypt = true`, `use_lockfile = true`; document the partial configuration (bucket, region, `kms_key_id` passed via `-backend-config`) and `-backend=false` for local and CI validation
- [x] 1.3 Create `infra/terraform/variables.tf` — 18 typed and described inputs: `aws_region`, `project_name`, `environment`, `api_stage_name`, `log_retention_days`, `log_level`, `lambda_memory_size`, `lambda_timeout_seconds`, `lambda_architecture`, `lambda_source_dir`, `layer_source_dir`, `api_throttle_rate_limit`, `api_throttle_burst_limit`, `api_quota_limit`, `api_quota_period`, `dlq_retention_seconds`, `kms_key_arn`, `additional_tags`
- [x] 1.4 Add `validation` blocks to the seven constrained inputs — `environment` (dev/staging/prod), `log_retention_days` (CloudWatch-supported periods), `log_level` (Powertools levels), `lambda_memory_size` (128–10240), `lambda_timeout_seconds` (1–60, capped by the technology guidelines), `lambda_architecture` (arm64/x86_64), `api_quota_period` (DAY/WEEK/MONTH)
- [x] 1.5 Create `infra/terraform/locals.tf` — `name_prefix = "${var.project_name}-${var.environment}"`; `common_tags` with Project, Environment, ManagedBy, Feature and Repository merged with `var.additional_tags`; `source_root` resolved as `abspath("${path.root}/../..")` so defaults work from any invocation directory; `lambda_source_dir` and `layer_source_dir` defaulted with `coalesce` to `src/functions` and `src/layers/common`
- [x] 1.6 Create `infra/terraform/main.tf` — `provider "aws"` on `var.aws_region` and a single `module "ingestion"` block passing naming, tags, packaging, Lambda sizing, logging, API and DLQ inputs
- [x] 1.7 Create `infra/terraform/outputs.tf` — re-export nine module outputs: `events_endpoint_url`, `api_id`, `api_key_id`, `usage_plan_id`, `lambda_function_name`, `lambda_function_arn`, `lambda_log_group_name`, `common_layer_arn`, `dead_letter_queue_url`
- [x] 1.8 Create `infra/terraform/environments/dev.tfvars` — `us-east-1`, `streamprocess`/`dev`, stage `v1`, 50/100 throttle, 100000 `MONTH` quota, 256 MB / 30 s / arm64, `INFO` at 14-day retention, `kms_key_arn = null` with a comment that dev accepts AWS managed keys while staging and prod must pass a CMK, plus `CostCenter` and `Owner` tags

### Task 2: Ingestion Module — Scaffolding, Packaging and DLQ

- [x] 2.1 Create `infra/terraform/modules/ingestion/versions.tf` — `terraform >= 1.14`, `hashicorp/aws ~> 5.0`, `hashicorp/archive ~> 2.4`
- [x] 2.2 Create `infra/terraform/modules/ingestion/variables.tf` — 19 typed and described inputs; `name_prefix`, `environment`, `tags`, `lambda_source_dir` and `layer_source_dir` required with no default, the remainder defaulted (`lambda_handler = "ingest.handler.handler"`, `lambda_runtime = "python3.12"`, `lambda_architecture = "arm64"`, `lambda_memory_size = 256`, `lambda_timeout_seconds = 30`, `log_level = "INFO"`, `log_retention_days = 14`, `api_stage_name = "v1"`, throttle 50/100, quota 100000/`MONTH`, `dlq_retention_seconds = 1209600`, `kms_key_arn = null`)
- [x] 2.3 Create `infra/terraform/modules/ingestion/main.tf` with a `locals` block — `function_name = "${var.name_prefix}-ingest-api"`, `service_name = "${var.name_prefix}-ingest"`, `api_name = "${var.name_prefix}-ingestion-api"`, `dlq_name = "${var.name_prefix}-ingest-dlq"`
- [x] 2.4 Add `data "archive_file" "function"` and `data "archive_file" "layer"` — zips rooted at the two source dirs so `ingest/` sits at the package root and the layer's `python/` maps to `/opt/python`; excludes `**/__pycache__/**`, `**/*.pyc`, and `**/requirements.txt` for the function archive; outputs written under `${path.module}/build/`
- [x] 2.5 Add a header comment documenting the packaging contract, explaining why the function stays a package so its `models` module cannot shadow the layer's
- [x] 2.6 Add `aws_sqs_queue "dlq"` — `message_retention_seconds` from `var.dlq_retention_seconds` (14 days), `kms_master_key_id` set from `var.kms_key_arn`, `sqs_managed_sse_enabled` when that is `null`, tagged with `var.tags`. Required by `infra-guidelines.md`, which mandates an SQS DLQ for every Lambda function.

### Task 3: Least-Privilege Execution Role

- [x] 3.1 Add `data "aws_iam_policy_document" "lambda_assume_role"` — `sts:AssumeRole` for the `lambda.amazonaws.com` service principal
- [x] 3.2 Add `aws_iam_role "lambda"` — named `${local.function_name}-role` with a description and `var.tags`
- [x] 3.3 Add `data "aws_iam_policy_document" "lambda"` statement `WriteFunctionLogs` — `logs:CreateLogStream` and `logs:PutLogEvents` scoped to `"${aws_cloudwatch_log_group.lambda.arn}:*"`; deliberately no `logs:CreateLogGroup`, since Terraform owns the group
- [x] 3.4 Add statement `PublishTraceSegments` — `xray:PutTraceSegments` and `xray:PutTelemetryRecords` on `*`, with a comment noting X-Ray segment ingestion has no resource-level permissions
- [x] 3.5 Add statement `SendToDeadLetterQueue` — `sqs:SendMessage` scoped to `aws_sqs_queue.dlq.arn` only
- [x] 3.6 Add a `dynamic "statement"` for `UseCustomerManagedKey` — `kms:Decrypt` and `kms:GenerateDataKey` on `var.kms_key_arn`, emitted only when a CMK is supplied
- [x] 3.7 Add `aws_iam_role_policy "lambda"` — inline policy `${local.function_name}-policy` attached to the role

### Task 4: Function, Layer and Log Group

- [x] 4.1 Add `aws_cloudwatch_log_group "lambda"` — `/aws/lambda/${local.function_name}`, `retention_in_days` from `var.log_retention_days`, `kms_key_id` from `var.kms_key_arn`, tagged
- [x] 4.2 Add `aws_lambda_layer_version "common"` — `${var.name_prefix}-common`, `filename` and `source_code_hash` from the layer archive, `compatible_runtimes` and `compatible_architectures` from the runtime and architecture variables
- [x] 4.3 Add `aws_lambda_function "ingest"` — `${local.function_name}`, handler, runtime, architecture, memory, timeout and layer from variables; `filename` and `source_code_hash` from the function archive; `tracing_config` mode `Active`
- [x] 4.4 Add `dead_letter_config` to the function targeting `aws_sqs_queue.dlq.arn`, with a comment that story E2 also routes schema-invalid events to the same queue from inside the handler
- [x] 4.5 Add the function `environment` block — `ENVIRONMENT`, `LOG_LEVEL`, `POWERTOOLS_SERVICE_NAME`, `POWERTOOLS_METRICS_NAMESPACE` set to `StreamProcess/${var.environment}`, `POWERTOOLS_LOGGER_LOG_EVENT` `"false"`, and `EVENT_DLQ_URL`
- [x] 4.6 Add `depends_on` for the log group and the role policy so the function is not created before it can write logs
- [x] 4.7 Add `aws_lambda_permission "api_gateway"` — `lambda:InvokeFunction` for `apigateway.amazonaws.com`, `source_arn` scoped to the API execution ARN for the `POST` method on `/events`

### Task 5: REST API, Stage, Key and Usage Plan

- [x] 5.1 Add `aws_api_gateway_rest_api "this"` — `${local.api_name}` with a `REGIONAL` `endpoint_configuration` and tags
- [x] 5.2 Add `aws_api_gateway_resource "events"` — `path_part = "events"` off the API root
- [x] 5.3 Add `aws_api_gateway_method "post_events"` — `POST`, `authorization = "NONE"`, `api_key_required = true`, with a comment that unkeyed requests get 403 before the function runs
- [x] 5.4 Add `aws_api_gateway_integration "lambda"` — `type = "AWS_PROXY"`, `integration_http_method = "POST"`, `uri` from the function's `invoke_arn`
- [x] 5.5 Add `aws_api_gateway_deployment "this"` — `triggers.redeployment` hashed from the resource, method and integration IDs, with `create_before_destroy = true`
- [x] 5.6 Add `aws_api_gateway_stage "this"` — stage from `var.api_stage_name`, environment-specific description, `xray_tracing_enabled = true`, tagged
- [x] 5.7 Add `aws_api_gateway_method_settings "this"` on `*/*` — `metrics_enabled = true`, `data_trace_enabled = false`, throttling from `var.api_throttle_rate_limit` and `var.api_throttle_burst_limit`, and `logging_level = "OFF"` with a comment explaining that execution and access logging need an account-level API Gateway CloudWatch role this module does not own
- [x] 5.8 Add `aws_api_gateway_api_key "publisher"` — `${var.name_prefix}-publisher`, enabled, described as rotated quarterly per the security baseline
- [x] 5.9 Add `aws_api_gateway_usage_plan "this"` — bound to the API and stage via `api_stages`, with `throttle_settings` and `quota_settings` from variables
- [x] 5.10 Add `aws_api_gateway_usage_plan_key "publisher"` — associate the API key with the usage plan

### Task 6: Module Outputs and Documentation

- [x] 6.1 Create `infra/terraform/modules/ingestion/outputs.tf` — 13 described outputs: `api_id`, `api_execution_arn`, `api_invoke_url`, `events_endpoint_url`, `api_key_id`, `usage_plan_id`, `lambda_function_name`, `lambda_function_arn`, `lambda_role_arn`, `lambda_log_group_name`, `common_layer_arn`, `dead_letter_queue_url`, `dead_letter_queue_arn`
- [x] 6.2 Confirm the API key *value* is not exported — only `api_key_id`, with the output description pointing at `aws apigateway get-api-key --include-value` or SSM `SecureString`
- [x] 6.3 Create `infra/terraform/modules/ingestion/README.md` — purpose, story ownership, and a "What it creates" table mapping each resource type in the module to its role in the stack
- [x] 6.4 Document the usage example and the packaging contract in the README, including the CI `pip install --platform manylinux2014_aarch64 --python-version 3.12 --only-binary=:all:` step needed because `archive_file` does not bundle `requirements.txt` dependencies
- [x] 6.5 Document the inputs and outputs tables in the README
- [x] 6.6 Document the known gaps in the README — API key value never an output, `logging_level = "OFF"` pending the account-level CloudWatch role, optional CMK for dev only, request validation living in the handler, and no provisioned concurrency

### Task 7: Validation

- [x] 7.1 `terraform fmt -check -recursive` in `infra/terraform/` — passes for the root composition and the module
- [x] 7.2 `terraform init -backend=false && terraform validate` — passes with no errors
- [x] 7.3 `tflint` on the root composition and the ingestion module — no findings
- [x] 7.4 `terraform plan -var-file=environments/dev.tfvars` — shows the expected API Gateway, Lambda, layer, log group, IAM and SQS resources and no unexpected deletions
