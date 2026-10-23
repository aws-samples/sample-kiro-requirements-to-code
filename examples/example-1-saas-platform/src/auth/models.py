"""Typed representation of an authenticated caller."""

from pydantic import BaseModel, ConfigDict, Field


class CurrentUser(BaseModel):
    """Claims extracted from a verified Cognito ID token.

    Injected into route handlers by :func:`auth.dependencies.get_current_user`.
    Immutable so downstream code (RBAC in A3, tenant routing in A4) cannot
    mutate the authenticated identity mid-request.

    Attributes:
        sub: Cognito subject id, the stable unique user identifier.
        email: Email address of the user.
        tenant_id: Tenant the user belongs to, from the ``custom:tenant_id`` claim.
        role: Role name, from the ``custom:role`` claim. Enforced in story A3.
    """

    model_config = ConfigDict(frozen=True, extra="ignore")

    sub: str = Field(min_length=1, description="Cognito subject id.")
    email: str = Field(min_length=1, description="User email address.")
    tenant_id: str = Field(min_length=1, description="Tenant id from custom:tenant_id.")
    role: str = Field(min_length=1, description="Role name from custom:role.")
