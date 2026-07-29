"""FastAPI dependency — reads the session cookie and returns the current User."""

from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.config import get_settings
from app.database import get_db
from app.models.user import User

_PLACEHOLDER_EMAIL = "placeholder@internal"


def _get_placeholder_user(db: Session) -> User:
    user = db.query(User).filter(User.email == _PLACEHOLDER_EMAIL).first()
    if not user:
        user = User(email=_PLACEHOLDER_EMAIL, hashed_password=None)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_current_user(
    session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    When REQUIRE_AUTH=false (Vercel / local dev): returns placeholder user, no login needed.
    When REQUIRE_AUTH=true (VM): validates the session cookie set by the OAuth callback.
    """
    settings = get_settings()

    if not settings.require_auth:
        return _get_placeholder_user(db)

    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated.")

    try:
        claims = jwt.decode(session, settings.app_secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    user = db.query(User).filter(User.id == claims.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    return user


