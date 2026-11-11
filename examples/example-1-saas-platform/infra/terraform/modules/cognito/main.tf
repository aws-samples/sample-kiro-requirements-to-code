#
# Cognito identity provider for TaskFlow (story A1, DEC-001).
#
# Provisions a user pool with tenant-aware custom attributes, an OAuth2
# Authorization Code + PKCE app client, and a hosted-UI domain. The JWT
# middleware (story A2) validates tokens against this pool's JWKS endpoint.
#
# MFA is configured but optional — enforcement is deferred to PI 2, as are
# social identity providers and the custom login UI.
#

data "aws_region" "current" {}

# ---------------------------------------------------------------------------
# User pool
# ---------------------------------------------------------------------------

resource "aws_cognito_user_pool" "main" {
  name = "${var.name_prefix}-users"

  # Email is the login identifier; no separate username to keep in sync.
  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  deletion_protection = var.environment == "prod" ? "ACTIVE" : "INACTIVE"

  username_configuration {
    case_sensitive = false
  }

  password_policy {
    minimum_length                   = var.password_min_length
    require_lowercase                = true
    require_numbers                  = true
    require_symbols                  = true
    require_uppercase                = true
    temporary_password_validity_days = 7
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  # Self-signup is disabled until an invitation / tenant-provisioning flow
  # exists. Users are created by an admin or automation (AdminCreateUser), which
  # is also the only path that can set custom:tenant_id.
  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  # TOTP registered so MFA can be turned on per user without replacing the pool.
  mfa_configuration = "OPTIONAL"

  software_token_mfa_configuration {
    enabled = true
  }

  # Tenant binding. Immutable by design: a user cannot be moved between tenants
  # by an attribute update, only by re-provisioning. This is the boundary the
  # tenant isolation middleware (story A4) trusts.
  schema {
    name                     = "tenant_id"
    attribute_data_type      = "String"
    mutable                  = false
    required                 = false
    developer_only_attribute = false

    string_attribute_constraints {
      min_length = 1
      max_length = 64
    }
  }

  # Application role, resolved by the RBAC dependency (story A3). Mutable so a
  # tenant admin can promote or demote a user without recreating the account.
  schema {
    name                     = "role"
    attribute_data_type      = "String"
    mutable                  = true
    required                 = false
    developer_only_attribute = false

    string_attribute_constraints {
      min_length = 1
      max_length = 32
    }
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-users"
  })
}

# ---------------------------------------------------------------------------
# App client
# ---------------------------------------------------------------------------

resource "aws_cognito_user_pool_client" "app" {
  name         = "${var.name_prefix}-app-client"
  user_pool_id = aws_cognito_user_pool.main.id

  # Confidential client: the secret stays server-side in the API tier.
  generate_secret = true

  # Authorization Code grant only. "implicit" is deliberately absent, so
  # Cognito will not issue tokens on the redirect. Clients send an S256
  # code_challenge to /oauth2/authorize; Cognito accepts PKCE on the code flow
  # with no extra server-side configuration.
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  supported_identity_providers         = ["COGNITO"]

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls

  # SRP for direct sign-in, refresh for session renewal. USER_PASSWORD_AUTH and
  # the legacy non-ALLOW_ flows stay off so passwords never transit the API.
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
  ]

  access_token_validity  = 60
  id_token_validity      = 60
  refresh_token_validity = 30

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  enable_token_revocation       = true
  prevent_user_existence_errors = "ENABLED"

  read_attributes = [
    "email",
    "email_verified",
    "custom:tenant_id",
    "custom:role",
  ]

  # custom:tenant_id is immutable and therefore cannot be a write attribute.
  # It is set once at provisioning time through the Cognito Admin API.
  #
  # custom:role is deliberately absent. It is set only server-side (via
  # AdminUpdateUserAttributes from a backend admin path, or Cognito groups) and
  # must never be user-writable: RBAC (story A3) will trust this claim, so a
  # user who could write it could make themselves admin.
  write_attributes = [
    "email",
  ]
}

# ---------------------------------------------------------------------------
# Hosted UI domain
# ---------------------------------------------------------------------------

# Prefix domains share a global namespace per region, so name_prefix must be
# unique across accounts. Replaced by a custom domain when the custom login UI
# ships in PI 2.
resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.name_prefix}-auth"
  user_pool_id = aws_cognito_user_pool.main.id
}
