output "events_endpoint_url" {
  description = "Full HTTPS URL event publishers POST to, including the stage and resource path."
  value       = module.ingestion.events_endpoint_url
}

output "api_id" {
  description = "Identifier of the ingestion REST API."
  value       = module.ingestion.api_id
}

output "publisher_invoke_policy_arn" {
  description = "IAM policy granting execute-api:Invoke on POST /events. Attach it to each publisher's role or user."
  value       = module.ingestion.publisher_invoke_policy_arn
}

output "api_key_id" {
  description = "Identifier of the publisher API key (metering only). Read the key value with the AWS CLI or console; it is never emitted as an output."
  value       = module.ingestion.api_key_id
}

output "usage_plan_id" {
  description = "Identifier of the usage plan that enforces the API key and throttling."
  value       = module.ingestion.usage_plan_id
}

output "lambda_function_name" {
  description = "Name of the ingestion Lambda function."
  value       = module.ingestion.lambda_function_name
}

output "lambda_function_arn" {
  description = "ARN of the ingestion Lambda function."
  value       = module.ingestion.lambda_function_arn
}

output "lambda_log_group_name" {
  description = "CloudWatch Logs group holding the ingestion Lambda logs."
  value       = module.ingestion.lambda_log_group_name
}

output "common_layer_arn" {
  description = "Versioned ARN of the shared common Lambda layer."
  value       = module.ingestion.common_layer_arn
}

output "dead_letter_queue_url" {
  description = "URL of the ingestion dead-letter queue."
  value       = module.ingestion.dead_letter_queue_url
}
