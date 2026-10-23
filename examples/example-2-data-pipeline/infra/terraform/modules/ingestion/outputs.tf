output "api_id" {
  description = "Identifier of the ingestion REST API."
  value       = aws_api_gateway_rest_api.this.id
}

output "api_execution_arn" {
  description = "Execution ARN of the REST API, used to scope Lambda invoke permissions."
  value       = aws_api_gateway_rest_api.this.execution_arn
}

output "api_invoke_url" {
  description = "Base invoke URL of the deployed stage."
  value       = aws_api_gateway_stage.this.invoke_url
}

output "events_endpoint_url" {
  description = "Full HTTPS URL event publishers POST to."
  value       = "${aws_api_gateway_stage.this.invoke_url}${aws_api_gateway_resource.events.path}"
}

output "api_key_id" {
  description = "Identifier of the publisher API key. The key value is intentionally not exposed as an output."
  value       = aws_api_gateway_api_key.publisher.id
}

output "usage_plan_id" {
  description = "Identifier of the usage plan enforcing the API key, throttling and quota."
  value       = aws_api_gateway_usage_plan.this.id
}

output "lambda_function_name" {
  description = "Name of the ingestion Lambda function."
  value       = aws_lambda_function.ingest.function_name
}

output "lambda_function_arn" {
  description = "ARN of the ingestion Lambda function."
  value       = aws_lambda_function.ingest.arn
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role."
  value       = aws_iam_role.lambda.arn
}

output "lambda_log_group_name" {
  description = "CloudWatch Logs group holding the ingestion Lambda logs."
  value       = aws_cloudwatch_log_group.lambda.name
}

output "common_layer_arn" {
  description = "Versioned ARN of the shared common Lambda layer."
  value       = aws_lambda_layer_version.common.arn
}

output "dead_letter_queue_url" {
  description = "URL of the ingestion dead-letter queue."
  value       = aws_sqs_queue.dlq.url
}

output "dead_letter_queue_arn" {
  description = "ARN of the ingestion dead-letter queue."
  value       = aws_sqs_queue.dlq.arn
}
