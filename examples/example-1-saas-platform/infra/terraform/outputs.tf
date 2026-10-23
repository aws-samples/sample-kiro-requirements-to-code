# ---------------------------------------------------------------------------
# Authentication (story A1)
#
# Consumed by the API service configuration (story A2) and by local development
# setup. The app client secret is deliberately not re-exported here — read it
# from Secrets Manager rather than from state.
# ---------------------------------------------------------------------------

output "cognito_user_pool_id" {
  description = "Cognito user pool ID for the API's token validation and admin calls."
  value       = module.cognito.user_pool_id
}

output "cognito_user_pool_arn" {
  description = "Cognito user pool ARN, for IAM policies scoped to this pool."
  value       = module.cognito.user_pool_arn
}

output "cognito_app_client_id" {
  description = "OAuth2 client_id, also the expected JWT audience claim."
  value       = module.cognito.app_client_id
}

output "cognito_jwks_url" {
  description = "JWKS endpoint the JWT middleware uses to verify token signatures."
  value       = module.cognito.jwks_url
}

output "cognito_user_pool_domain" {
  description = "Hosted UI domain prefix. Full URL: https://<domain>.auth.<region>.amazoncognito.com."
  value       = module.cognito.user_pool_domain
}

output "cognito_user_pool_endpoint" {
  description = "User pool endpoint host; the JWT issuer once prefixed with https://."
  value       = module.cognito.user_pool_endpoint
}
