output "user_pool_id" {
  description = "Cognito user pool ID. Consumed by the API for token validation and admin operations."
  value       = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  description = "Cognito user pool ARN. Used in IAM policies that scope admin actions to this pool."
  value       = aws_cognito_user_pool.main.arn
}

output "app_client_id" {
  description = "App client ID used as the OAuth2 client_id and as the expected JWT audience."
  value       = aws_cognito_user_pool_client.app.id
}

output "app_client_secret" {
  description = "App client secret. Store in Secrets Manager; never commit it or expose it to browser clients."
  value       = aws_cognito_user_pool_client.app.client_secret
  sensitive   = true
}

output "jwks_url" {
  description = "JWKS endpoint for verifying pool-issued JWT signatures (story A2 middleware)."
  value       = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${aws_cognito_user_pool.main.id}/.well-known/jwks.json"
}

output "user_pool_domain" {
  description = "Hosted UI domain prefix. Full URL is https://<domain>.auth.<region>.amazoncognito.com."
  value       = aws_cognito_user_pool_domain.main.domain
}

output "user_pool_endpoint" {
  description = "User pool endpoint host, also the JWT issuer once prefixed with https://."
  value       = aws_cognito_user_pool.main.endpoint
}
