# Module — ingestion

REST ingestion stack for StreamProcess feature 101: an API Gateway REST API with
`POST /events`, API key authentication through a usage plan, the ingestion Lambda
from story E1, its shared layer, a dead-letter queue and a log group.

Story E4 owns this module. Kinesis persistence (E3) and schema validation (E2)
extend it later.

## What it creates

| Resource | Purpose |
|----------|---------|
| `aws_api_gateway_rest_api` + `aws_api_gateway_resource` + `aws_api_gateway_method` | Regional REST API exposing `POST /events` with `api_key_required = true` |
| `aws_api_gateway_integration` | `AWS_PROXY` integration to the ingestion Lambda |
| `aws_api_gateway_deployment` + `aws_api_gateway_stage` | Deployed stage with X-Ray tracing enabled |
| `aws_api_gateway_method_settings` | CloudWatch metrics and per-method throttling |
| `aws_api_gateway_api_key` + `aws_api_gateway_usage_plan` + `aws_api_gateway_usage_plan_key` | Publisher API key, throttling and quota |
| `aws_lambda_function` | Ingestion handler, X-Ray tracing `Active`, DLQ attached |
| `aws_lambda_layer_version` | Shared `common` layer (config, models, RFC 7807 helpers) |
| `aws_cloudwatch_log_group` | Function logs, 14-day retention in dev |
| `aws_iam_role` + `aws_iam_role_policy` | Least-privilege execution role |
| `aws_sqs_queue` | Dead-letter queue, 14-day retention |

## Usage

```hcl
module "ingestion" {
  source = "./modules/ingestion"

  name_prefix = "streamprocess-dev"
  environment = "dev"
  tags        = local.common_tags

  lambda_source_dir = "${path.root}/../../src/functions"
  layer_source_dir  = "${path.root}/../../src/layers/common"
}
```

## Packaging contract

- The function archive is rooted at `lambda_source_dir`, so `ingest/` sits at the
  top of the zip and the handler is `ingest.handler.handler`. Keeping the
  function as a package means its `models` module cannot shadow the layer's.
- The layer archive is rooted at `layer_source_dir`, which contains `python/`.
  That directory becomes `/opt/python`, so `config`, `models` and `responses`
  resolve as top-level imports.
- `archive_file` zips whatever is in those directories and nothing else. Runtime
  dependencies from `src/functions/ingest/requirements.txt` are **not** included,
  so CI installs them into a build directory and points `lambda_source_dir` at
  it:

  ```bash
  pip install -r src/functions/ingest/requirements.txt \
    --target build/functions --platform manylinux2014_aarch64 \
    --implementation cp --python-version 3.12 --only-binary=:all:
  cp -r src/functions/ingest build/functions/
  ```

  Compiled wheels (`pydantic-core`) must match `lambda_architecture`.

## Inputs

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name_prefix` | `string` | — | Prefix for every resource name |
| `environment` | `string` | — | Deployment environment, published as `ENVIRONMENT` |
| `tags` | `map(string)` | — | Common tags applied to every taggable resource |
| `lambda_source_dir` | `string` | — | Directory zipped into the function package |
| `layer_source_dir` | `string` | — | Directory zipped into the layer, must contain `python/` |
| `lambda_handler` | `string` | `ingest.handler.handler` | Function entry point |
| `lambda_runtime` | `string` | `python3.12` | Lambda runtime |
| `lambda_architecture` | `string` | `arm64` | Instruction set for function and layer |
| `lambda_memory_size` | `number` | `256` | Memory in MB |
| `lambda_timeout_seconds` | `number` | `30` | Timeout in seconds |
| `log_level` | `string` | `INFO` | Powertools log level |
| `log_retention_days` | `number` | `14` | Log group retention |
| `api_stage_name` | `string` | `v1` | Stage name and first path segment |
| `api_throttle_rate_limit` | `number` | `50` | Requests per second per key |
| `api_throttle_burst_limit` | `number` | `100` | Burst capacity per key |
| `api_quota_limit` | `number` | `100000` | Requests per quota period |
| `api_quota_period` | `string` | `MONTH` | `DAY`, `WEEK` or `MONTH` |
| `dlq_retention_seconds` | `number` | `1209600` | DLQ retention (14 days) |
| `kms_key_arn` | `string` | `null` | CMK for the DLQ and log group |

## Outputs

| Name | Description |
|------|-------------|
| `api_id` | REST API identifier |
| `api_execution_arn` | Execution ARN used to scope invoke permissions |
| `api_invoke_url` | Base invoke URL of the stage |
| `events_endpoint_url` | Full URL publishers POST to |
| `api_key_id` | Publisher API key identifier |
| `usage_plan_id` | Usage plan identifier |
| `lambda_function_name` | Ingestion function name |
| `lambda_function_arn` | Ingestion function ARN |
| `lambda_role_arn` | Execution role ARN |
| `lambda_log_group_name` | Function log group |
| `common_layer_arn` | Versioned layer ARN |
| `dead_letter_queue_url` | DLQ URL |
| `dead_letter_queue_arn` | DLQ ARN |

## Notes and known gaps

- **API key value is never an output.** Only `api_key_id` is exported. Read the
  value with `aws apigateway get-api-key --include-value`, or move it into SSM
  Parameter Store as a `SecureString` per the security baseline.
- **API Gateway logging is `OFF`.** Execution and access logging require an
  account-level `aws_api_gateway_account.cloudwatch_role_arn`, which is global
  state this module deliberately does not own. Set it once per account, then
  raise `logging_level` to `ERROR` or add `access_log_settings`.
- **Encryption.** `kms_key_arn` is optional so dev can run on AWS managed keys.
  Staging and prod must pass a customer managed key.
- **Request validation lives in the Lambda.** Content-Type and empty-body checks
  return RFC 7807 Problem Details from the handler, which is what story E1's
  acceptance criteria specify. No API Gateway request validator is attached.
- **Provisioned concurrency** is not configured. Cold starts are accepted in dev
  per design.md, open question 1.
