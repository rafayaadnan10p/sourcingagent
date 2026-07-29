"""FastAPI dependency that validates the Microsoft Bearer token and returns the User."""

import uuid
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from jose import JWTError

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.auth.microsoft import validate_microsoft_token

_PLACEHOLDER_EMAIL = "placeholder@internal"


def _get_placeholder_user(db: Session) -> User:
    """Returns the shared placeholder user used when auth is disabled."""
    user = db.query(User).filter(User.email == _PLACEHOLDER_EMAIL).first()
    if not user:
        user = User(email=_PLACEHOLDER_EMAIL, hashed_password=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    When REQUIRE_AUTH=false (Vercel / Render / local dev):
      returns the shared placeholder user — no token needed, existing behaviour unchanged.

    When REQUIRE_AUTH=true (VM / production):
      validates the Microsoft Bearer token, creates the user on first login.
    """
    settings = get_settings()

    if not settings.require_auth:
        return _get_placeholder_user(db)

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")

    token = authorization.split(" ", 1)[1]
    try:
        claims = validate_microsoft_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {exc}")
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed.")

    azure_oid: str = claims.get("oid", "")
    email: str = (
        claims.get("preferred_username")
        or claims.get("email")
        or claims.get("upn")
        or ""
    )

    if not azure_oid:
        raise HTTPException(status_code=401, detail="Token missing required claims.")

    user = db.query(User).filter(User.azure_oid == azure_oid).first()
    if not user:
        user = User(email=email, azure_oid=azure_oid, hashed_password=None)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

