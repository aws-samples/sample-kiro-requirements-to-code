# Cognito Module

AWS Cognito user pool for TaskFlow: tenant-aware custom attributes, an OAuth2
Authorization Code + PKCE app client, and a hosted-UI domain.

Implements DEC-001 (Cognito as the identity provider) from
`.kiro/specs/101-authentication/design.md`.

## What it creates

| Resource | Notes |
|----------|-------|
| `aws_cognito_user_pool` | Email login, password policy, email account recovery, TOTP MFA available but optional |
| `aws_cognito_user_pool_client` | Confidential client, code grant only, token revocation, `prevent_user_existence_errors` on |
| `aws_cognito_user_pool_domain` | Hosted UI at `<name_prefix>-auth` |

### Custom attributes

| Attribute | Type | Mutable | Why |
|-----------|------|---------|-----|
| `custom:tenant_id` | String (1-64) | No | Tenant binding. Immutability is the boundary tenant isolation (A4) trusts — moving a user between tenants requires re-provisioning. |
| `custom:role` | String (1-32) | Yes | Application role read by the RBAC dependency (A3). Tenant admins can promote or demote users in place. |

Because `custom:tenant_id` is immutable it is **not** in the client's
`write_attributes`. Set it once at provisioning time with the Cognito Admin API
(`AdminCreateUser` / `AdminUpdateUserAttributes`).

Custom attributes cannot be renamed, retyped, or removed after the pool exists.
Changing either `schema` block replaces the user pool and every user in it.

### OAuth2 configuration

- `allowed_oauth_flows = ["code"]` — implicit grant is disabled.
- PKCE: clients send an S256 `code_challenge` to `/oauth2/authorize`. Cognito
  accepts PKCE on the code flow with no extra server-side setting, which is why
  there is no `pkce` argument to configure.
- `explicit_auth_flows` allows SRP and refresh only, so raw passwords never
  reach the API tier.
- Access and ID tokens live 60 minutes; refresh tokens 30 days.

## Usage

```hcl
module "cognito" {
  source = "./modules/cognito"

  name_prefix = local.name_prefix
  environment = var.environment

  callback_urls = ["https://app.example.com/callback"]
  logout_urls   = ["https://app.example.com/logout"]

  password_min_length = 12

  tags = local.common_tags
}
```

## Inputs

| Name | Type | Default | Required | Description |
|------|------|---------|:--------:|-------------|
| `name_prefix` | `string` | — | yes | Prefix for all resource names, e.g. `taskflow-dev`. Also the hosted UI domain prefix, so it must be DNS-safe. |
| `environment` | `string` | — | yes | `dev`, `staging`, or `prod`. Enables deletion protection on `prod`. |
| `callback_urls` | `list(string)` | — | yes | Allowed OAuth2 redirect URIs. HTTPS only, except `http://localhost`. |
| `logout_urls` | `list(string)` | — | yes | Allowed sign-out redirect URIs. Same scheme rules. |
| `password_min_length` | `number` | `12` | no | Minimum password length (8-99). Upper, lower, number, and symbol are always required. |
| `tags` | `map(string)` | `{}` | no | Tags applied to every taggable resource, merged with a `Name` tag. |

## Outputs

| Name | Sensitive | Description |
|------|:---------:|-------------|
| `user_pool_id` | no | User pool ID. |
| `user_pool_arn` | no | User pool ARN, for IAM policies scoped to this pool. |
| `app_client_id` | no | OAuth2 `client_id`, also the expected JWT audience. |
| `app_client_secret` | yes | Client secret. Store in Secrets Manager; never expose to browser clients. |
| `jwks_url` | no | JWKS endpoint used by the JWT middleware (A2). |
| `user_pool_domain` | no | Hosted UI domain prefix. Full URL: `https://<domain>.auth.<region>.amazoncognito.com`. |
| `user_pool_endpoint` | no | Endpoint host; the JWT issuer once prefixed with `https://`. |

## Out of scope

Custom login UI, social identity providers, MFA enforcement, and tenant
provisioning automation. See the A1 story for the full boundary.
