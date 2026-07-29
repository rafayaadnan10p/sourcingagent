"""Microsoft Azure AD JWT validation.

Validates ID tokens issued by Microsoft for the 10Pearls tenant.
JWKS keys are fetched from Microsoft's discovery endpoint and cached for 1 hour.
"""

import time
import httpx
from jose import jwt, JWTError
from app.config import get_settings

# In-memory JWKS cache — avoids fetching keys on every request
_jwks_cache: dict = {}
_jwks_expiry: float = 0.0
_JWKS_TTL = 3600  # seconds


def _get_jwks() -> dict:
    """Fetch (or return cached) Microsoft's public signing keys."""
    global _jwks_cache, _jwks_expiry
    if time.time() < _jwks_expiry and _jwks_cache:
        return _jwks_cache

    settings = get_settings()
    url = (
        f"https://login.microsoftonline.com"
        f"/{settings.azure_tenant_id}/discovery/v2.0/keys"
    )
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    _jwks_cache = response.json()
    _jwks_expiry = time.time() + _JWKS_TTL
    return _jwks_cache


def validate_microsoft_token(token: str) -> dict:
    """
    Decode and validate a Microsoft ID token.

    Returns the token claims dict on success.
    Raises jose.JWTError (or subclass) on any validation failure.
    """
    settings = get_settings()
    jwks = _get_jwks()

    claims = jwt.decode(
        token,
        jwks,
        algorithms=["RS256"],
        audience=settings.azure_client_id,
        options={"verify_exp": True},
    )
    return claims
