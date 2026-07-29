"""Server-side Microsoft OAuth flow for Web-platform app registrations.

Flow:
  1. GET /auth/login       — browser is redirected to Microsoft login page
  2. GET /auth/callback    — Microsoft returns here with ?code=...; backend exchanges
                             code for tokens using client_secret, sets session cookie
  3. GET /auth/me          — frontend checks this to know if user is logged in
  4. GET /auth/logout      — clears session cookie
"""

import urllib.parse
import httpx
from fastapi import APIRouter, Depends, HTTPException, Cookie, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.config import get_settings
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


def _build_auth_url() -> str:
    settings = get_settings()
    params = {
        "client_id":     settings.azure_client_id,
        "response_type": "code",
        "redirect_uri":  f"{settings.app_base_url}/auth/callback",
        "scope":         "openid profile email",
        "response_mode": "query",
    }
    base = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/authorize"
    return f"{base}?{urllib.parse.urlencode(params)}"


@router.get("/login")
def login():
    """Redirect browser to Microsoft's login page."""
    return RedirectResponse(_build_auth_url(), status_code=302)


@router.get("/callback")
def callback(
    code:  str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Receive the auth code from Microsoft, exchange it for tokens using the client secret,
    create / fetch the user, issue a signed session cookie, redirect to frontend root.
    """
    settings = get_settings()

    if error:
        return RedirectResponse(f"{settings.app_base_url}/?auth_error={error}", status_code=302)
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code in callback.")

    # Exchange code for tokens (server-side using client_secret — requires Web app type)
    token_resp = httpx.post(
        f"https://login.microsoftonline.com/{settings.azure_tenant_id}/oauth2/v2.0/token",
        data={
            "client_id":     settings.azure_client_id,
            "client_secret": settings.azure_client_secret,
            "code":          code,
            "redirect_uri":  f"{settings.app_base_url}/auth/callback",
            "grant_type":    "authorization_code",
        },
        timeout=15,
    )
    if token_resp.status_code != 200:
        print(f"[auth] Token exchange failed {token_resp.status_code}: {token_resp.text[:300]}")
        raise HTTPException(status_code=401, detail="Failed to exchange code for tokens.")

    tokens = token_resp.json()
    id_token = tokens.get("id_token")
    if not id_token:
        raise HTTPException(status_code=401, detail="No ID token in Microsoft response.")

    # Decode claims — no signature check needed (we trust our own token request)
    claims = jwt.get_unverified_claims(id_token)
    azure_oid = claims.get("oid", "")
    email     = claims.get("preferred_username") or claims.get("email") or ""

    if not azure_oid:
        raise HTTPException(status_code=401, detail="Could not extract user identity from token.")

    # Auto-create user on first login
    user = db.query(User).filter(User.azure_oid == azure_oid).first()
    if not user:
        user = User(email=email, azure_oid=azure_oid, hashed_password=None)
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"[auth] New user created: {email}")

    # Issue a signed HTTP-only session cookie (24 h)
    session_token = jwt.encode(
        {"user_id": str(user.id), "email": user.email},
        settings.app_secret_key,
        algorithm="HS256",
    )

    response = RedirectResponse(settings.app_base_url, status_code=302)
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=86400,
    )
    return response


@router.get("/me")
def me(session: str | None = Cookie(default=None), db: Session = Depends(get_db)):
    """Return current user info if session cookie is valid — used by the frontend."""
    if not session:
        raise HTTPException(status_code=401, detail="Not logged in.")
    try:
        settings = get_settings()
        claims = jwt.decode(session, settings.app_secret_key, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session.")

    user = db.query(User).filter(User.id == claims.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    return {"id": str(user.id), "email": user.email}


@router.get("/logout")
def logout():
    """Clear session cookie and redirect to root (which shows the login page)."""
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("session", httponly=True, secure=True, samesite="lax")
    return response
