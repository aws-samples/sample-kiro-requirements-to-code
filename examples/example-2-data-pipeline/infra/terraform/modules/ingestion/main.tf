locals {
  function_name = "${var.name_prefix}-ingest-api"
  service_name  = "${var.name_prefix}-ingest"
  api_name      = "${var.name_prefix}-ingestion-api"
  dlq_name      = "${var.name_prefix}-ingest-dlq"
}

# ---------------------------------------------------------------------------
# Packaging
#
# The function archive is rooted at var.lambda_source_dir, so ingest/ sits at the
# top of the zip and the handler is ingest.handler.handler. The layer archive is
# rooted at var.layer_source_dir, which holds python/, so the shared modules
# resolve as top-level imports from /opt/python.
# ---------------------------------------------------------------------------

data "archive_file" "function" {
  type        = "zip"
  source_dir  = var.lambda_source_dir
  output_path = "${path.module}/build/${local.function_name}.zip"
  excludes    = ["**/__pycache__/**", "**/*.pyc", "**/requirements.txt"]
}

data "archive_file" "layer" {
  type        = "zip"
  source_dir  = var.layer_source_dir
  output_path = "${path.module}/build/${var.name_prefix}-common-layer.zip"
  excludes    = ["**/__pycache__/**", "**/*.pyc"]
}

# ---------------------------------------------------------------------------
# Dead-letter queue
# ---------------------------------------------------------------------------

resource "aws_sqs_queue" "dlq" {
  name                      = local.dlq_name
  message_retention_seconds = var.dlq_retention_seconds
  kms_master_key_id         = var.kms_key_arn
  sqs_managed_sse_enabled   = var.kms_key_arn == null
  tags                      = var.tags
}

# ---------------------------------------------------------------------------
# Execution role
# ---------------------------------------------------------------------------

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    sid     = "LambdaAssumeRole"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${local.function_name}-role"
  description        = "Execution role for the StreamProcess ingestion Lambda."
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
  tags               = var.tags
}

data "aws_iam_policy_document" "lambda" {
  statement {
    sid       = "WriteFunctionLogs"
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.lambda.arn}:*"]
  }

  statement {
    sid     = "PublishTraceSegments"
    effect  = "Allow"
    actions = ["xray:PutTraceSegments", "xray:PutTelemetryRecords"]
    # X-Ray segment ingestion has no resource-level permissions.
    resources = ["*"]
  }

  statement {
    sid       = "SendToDeadLetterQueue"
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.dlq.arn]
  }

  dynamic "statement" {
    for_each = var.kms_key_arn == null ? [] : [var.kms_key_arn]

    content {
      sid       = "UseCustomerManagedKey"
      effect    = "Allow"
      actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
      resources = [statement.value]
    }
  }
}

resource "aws_iam_role_policy" "lambda" {
  name   = "${local.function_name}-policy"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda.json
}

# ---------------------------------------------------------------------------
# Function, layer and log group
# ---------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${local.function_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn
  tags              = var.tags
}

resource "aws_lambda_layer_version" "common" {
  layer_name               = "${var.name_prefix}-common"
  description              = "Shared models, config and RFC 7807 helpers for StreamProcess functions."
  filename                 = data.archive_file.layer.output_path
  source_code_hash         = data.archive_file.layer.output_base64sha256
  compatible_runtimes      = [var.lambda_runtime]
  compatible_architectures = [var.lambda_architecture]
}

resource "aws_lambda_function" "ingest" {
  function_name    = local.function_name
  description      = "Accepts events on POST /events, assigns a correlation ID and returns 202."
  role             = aws_iam_role.lambda.arn
  handler          = var.lambda_handler
  runtime          = var.lambda_runtime
  architectures    = [var.lambda_architecture]
  filename         = data.archive_file.function.output_path
  source_code_hash = data.archive_file.function.output_base64sha256
  memory_size      = var.lambda_memory_size
  timeout          = var.lambda_timeout_seconds
  layers           = [aws_lambda_layer_version.common.arn]
  tags             = var.tags

  tracing_config {
    mode = "Active"
  }

  # Asynchronous invocations that exhaust their retries land here. Story E2 also
  # routes schema-invalid events to this queue from inside the handler.
  dead_letter_config {
    target_arn = aws_sqs_queue.dlq.arn
  }

  environment {
    variables = {
      ENVIRONMENT                  = var.environment
      LOG_LEVEL                    = var.log_level
      POWERTOOLS_SERVICE_NAME      = local.service_name
      POWERTOOLS_METRICS_NAMESPACE = "StreamProcess/${var.environment}"
      POWERTOOLS_LOGGER_LOG_EVENT  = "false"
      EVENT_DLQ_URL                = aws_sqs_queue.dlq.url
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy.lambda,
  ]
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowInvokeFromIngestionApi"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.this.execution_arn}/*/${aws_api_gateway_method.post_events.http_method}${aws_api_gateway_resource.events.path}"
}

# ---------------------------------------------------------------------------
# REST API — POST /events
# ---------------------------------------------------------------------------

resource "aws_api_gateway_rest_api" "this" {
  name        = local.api_name
  description = "StreamProcess event ingestion API (feature 101)."
  tags        = var.tags

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "events" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "events"
}

resource "aws_api_gateway_method" "post_events" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.events.id
  http_method   = "POST"
  authorization = "NONE"
  # API key authentication: requests without x-api-key get 403 before the
  # function is invoked.
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.this.id
  resource_id             = aws_api_gateway_resource.events.id
  http_method             = aws_api_gateway_method.post_events.http_method
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  uri                     = aws_lambda_function.ingest.invoke_arn
}

resource "aws_api_gateway_deployment" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.events.id,
      aws_api_gateway_method.post_events.id,
      aws_api_gateway_integration.lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "this" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  deployment_id = aws_api_gateway_deployment.this.id
  stage_name    = var.api_stage_name
  description   = "Ingestion stage for ${var.environment}."
  tags          = var.tags

  xray_tracing_enabled = true
}

resource "aws_api_gateway_method_settings" "this" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_stage.this.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled        = true
    data_trace_enabled     = false
    throttling_rate_limit  = var.api_throttle_rate_limit
    throttling_burst_limit = var.api_throttle_burst_limit
    # Execution and access logging need an account-level API Gateway CloudWatch
    # role, which is not owned by this module. See README.md.
    logging_level = "OFF"
  }
}

# ---------------------------------------------------------------------------
# API key and usage plan
# ---------------------------------------------------------------------------

resource "aws_api_gateway_api_key" "publisher" {
  name        = "${var.name_prefix}-publisher"
  description = "API key issued to event publishers. Rotated quarterly."
  enabled     = true
  tags        = var.tags
}

resource "aws_api_gateway_usage_plan" "this" {
  name        = "${var.name_prefix}-ingestion-plan"
  description = "Throttling and quota for StreamProcess event publishers."
  tags        = var.tags

  api_stages {
    api_id = aws_api_gateway_rest_api.this.id
    stage  = aws_api_gateway_stage.this.stage_name
  }

  throttle_settings {
    rate_limit  = var.api_throttle_rate_limit
    burst_limit = var.api_throttle_burst_limit
  }

  quota_settings {
    limit  = var.api_quota_limit
    period = var.api_quota_period
  }
}

resource "aws_api_gateway_usage_plan_key" "publisher" {
  key_id        = aws_api_gateway_api_key.publisher.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.this.id
}
