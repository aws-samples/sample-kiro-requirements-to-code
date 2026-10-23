"""Environment-driven Cognito configuration (Feature 101, DEC-001).

Values come from the process environment only. Per
``.kiro/steering/technology-guidelines.md`` no secrets are read from ``.env``
files: the user pool id, region, and app client id are non-secret identifiers
injected by ECS task definitions from Terraform outputs.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Cognito user pool settings required to validate ID tokens.

    Attributes:
        user_pool_id: Cognito user pool id, for example ``us-east-1_aBcDeFgHi``.
        region: AWS region that hosts the user pool.
        app_client_id: Cognito app client id, used as the expected token audience.
    """

    model_config = SettingsConfigDict(env_prefix="COGNITO_", case_sensitive=False, extra="ignore")

    user_pool_id: str = Field(description="Cognito user pool id (env: COGNITO_USER_POOL_ID).")
    region: str = Field(description="AWS region hosting the user pool (env: COGNITO_REGION).")
    app_client_id: str = Field(description="Cognito app client id (env: COGNITO_APP_CLIENT_ID).")

    @property
    def issuer(self) -> str:
        """Return the expected ``iss`` claim for tokens from this user pool."""
        return f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"

    @property
    def jwks_url(self) -> str:
        """Return the JWKS document URL for this user pool."""
        return f"{self.issuer}/.well-known/jwks.json"


@lru_cache(maxsize=1)
def get_auth_settings() -> AuthSettings:
    """Return the process-wide :class:`AuthSettings`, built once and cached.

    Returns:
        The settings instance parsed from the environment.

    Raises:
        pydantic.ValidationError: If a required ``COGNITO_*`` variable is unset.
    """
    return AuthSettings()
