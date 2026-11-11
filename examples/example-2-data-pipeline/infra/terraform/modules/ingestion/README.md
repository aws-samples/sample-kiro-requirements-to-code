# Module — ingestion

REST ingestion stack for StreamProcess feature 101: an API Gateway REST API with
`POST /events` authenticated with IAM (SigV4), an API key and usage plan for
metering, the ingestion Lambda from story E1, its shared layer, a dead-letter
queue and log groups for the function and the gateway access log.

Story E4 owns this module. Kinesis persistence (E3) and schema validation (E2)
extend it later.

## What it creates

| Resource | Purpose |
|----------|---------|
| `aws_api_gateway_rest_api` + `aws_api_gateway_resource` + `aws_api_gateway_method` | Regional REST API exposing `POST /events` with `authorization = "AWS_IAM"` and `api_key_required = true` |
| `aws_iam_policy` (`publisher_invoke`) | Grants `execute-api:Invoke` on exactly `POST /events` of the stage; attach to publisher principals |
| `aws_api_gateway_integration` | `AWS_PROXY` integration to the ingestion Lambda |
| `aws_api_gateway_deployment` + `aws_api_gateway_stage` | Deployed stage with X-Ray tracing and JSON access logging enabled |
| `aws_cloudwatch_log_group` (`api_access`) | Access log per request: request ID, IAM caller, API key ID, status. No body or headers |
| `aws_api_gateway_method_settings` | CloudWatch metrics and per-method throttling |
| `aws_api_gateway_api_key` + `aws_api_gateway_usage_plan` + `aws_api_gateway_usage_plan_key` | Metering key, throttling and quota (not authentication) |
| `aws_lambda_function` | Ingestion handler, X-Ray tracing `Active`, DLQ attached |
| `aws_lambda_layer_version` | Shared `common` layer (config, models, RFC 7807 helpers) |
| `aws_cloudwatch_log_group` | Function logs, 14-day retention in dev |
| `aws_iam_role` + `aws_iam_role_policy` | Least-privilege execution role |
| `aws_sqs_queue` | Dead-letter queue, 14-day retention |

## Prerequisites

- **Account-level API Gateway CloudWatch role.** Access logging on the stage
  only works once `aws_api_gateway_account.cloudwatch_role_arn` is set. This is
  a per-account, per-region singleton, so the module does not create it. Apply
  it once per account (for example in a bootstrap root module):

  ```hcl
  data "aws_iam_policy_document" "apigw_logs_assume" {
    statement {
      actions = ["sts:AssumeRole"]
      principals {
        type        = "Service"
        identifiers = ["apigateway.amazonaws.com"]
      }
    }
  }

  resource "aws_iam_role" "apigw_logs" {
    name               = "api-gateway-cloudwatch-logs"
    assume_role_policy = data.aws_iam_policy_document.apigw_logs_assume.json
  }

  resource "aws_iam_role_policy_attachment" "apigw_logs" {
    role       = aws_iam_role.apigw_logs.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
  }

  resource "aws_api_gateway_account" "this" {
    cloudwatch_role_arn = aws_iam_role.apigw_logs.arn
  }
  ```

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

## Authentication: IAM (SigV4) plus a metering key

`POST /events` uses `authorization = "AWS_IAM"`. API Gateway verifies the SigV4
signature and the caller's IAM permissions before the Lambda is invoked, and the
caller identity is written to the access log. The API key is still required,
but only so the usage plan can throttle and meter per publisher; it is not an
authentication credential.

To onboard a publisher:

1. Attach the policy exported as `publisher_invoke_policy_arn` to the
   publisher's IAM role or user. It allows `execute-api:Invoke` on exactly
   `arn:<partition>:execute-api:<region>:<account>:<api-id>/<stage>/POST/events`.
2. Give the publisher the usage-plan key (see "Notes and known gaps").
3. The publisher signs each request with SigV4 and sends the key in `x-api-key`:

   ```bash
   awscurl --service execute-api --region "$AWS_REGION" -X POST \
     -H "Content-Type: application/json" -H "x-api-key: $API_KEY" \
     -d '{"type":"order.created","payload":{}}' "$EVENTS_ENDPOINT_URL"
   ```

Unsigned requests, requests signed by a principal without the policy, and
requests without a valid key are all rejected with 403 at the gateway.

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
| `log_retention_days` | `number` | `14` | Retention for the function and access log groups |
| `api_stage_name` | `string` | `v1` | Stage name and first path segment |
| `api_throttle_rate_limit` | `number` | `50` | Requests per second per key |
| `api_throttle_burst_limit` | `number` | `100` | Burst capacity per key |
| `api_quota_limit` | `number` | `100000` | Requests per quota period |
| `api_quota_period` | `string` | `MONTH` | `DAY`, `WEEK` or `MONTH` |
| `dlq_retention_seconds` | `number` | `1209600` | DLQ retention (14 days) |
| `kms_key_arn` | `string` | `null` | CMK for the DLQ and both log groups |

## Outputs

| Name | Description |
|------|-------------|
| `api_id` | REST API identifier |
| `api_execution_arn` | Execution ARN used to scope invoke permissions |
| `api_invoke_url` | Base invoke URL of the stage |
| `events_endpoint_url` | Full URL publishers POST to |
| `publisher_invoke_policy_arn` | IAM policy granting `execute-api:Invoke` on `POST /events` |
| `api_access_log_group_name` | API Gateway access log group |
| `api_key_id` | Publisher API key identifier (metering only) |
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
- **Execution logging is `OFF`; access logging is on.** The stage writes a
  JSON access log per request to `/aws/apigateway/<name_prefix>-access`. Both
  depend on the account-level role described under "Prerequisites". Raise
  `logging_level` to `ERROR` if integration-level traces are needed.
- **One metering key.** A single usage-plan key is shared by all publishers, so
  the key ID in the access log does not identify a publisher; the IAM `caller`
  and `userArn` fields do. Create one key per publisher if per-source quotas are
  required.
- **Encryption.** `kms_key_arn` is optional so dev can run on AWS managed keys.
  Staging and prod must pass a customer managed key; it covers the DLQ and both
  log groups.
- **Request validation lives in the Lambda.** Content-Type and empty-body checks
  return RFC 7807 Problem Details from the handler, which is what story E1's
  acceptance criteria specify. No API Gateway request validator is attached.
- **Provisioned concurrency** is not configured. Cold starts are accepted in dev
  per design.md, open question 1.
