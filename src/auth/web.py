
import os
import hmac
import hashlib
import secrets

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Request, Response

from src.auth.sessions import get_session_user


# Load the project environment variables.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET is missing from the .env file")


# Cookie names used by the application.
SESSION_COOKIE_NAME = "day16_session"
CSRF_COOKIE_NAME = "day16_csrf"

# Enable Secure cookies when the application uses HTTPS.
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"


def get_current_user(request: Request):
    """Identify the logged-in user from the session cookie."""

    # Read the session token from the browser cookie.
    session_token = request.cookies.get(SESSION_COOKIE_NAME)

    if not session_token:
        return None

    # Validate the token using the server-side database.
    return get_session_user(session_token)


def create_csrf_token() -> str:
    """Create a random CSRF token with a server-generated signature."""

    token = secrets.token_urlsafe(32)

    signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{token}.{signature}"


def validate_csrf_token(submitted_token: str, cookie_token: str) -> bool:
    """Validate the submitted CSRF token against its signed cookie."""

    if not submitted_token or not cookie_token:
        return False

    # The form token must match the browser's CSRF cookie.
    if not hmac.compare_digest(submitted_token, cookie_token):
        return False

    try:
        token, submitted_signature = cookie_token.rsplit(".", 1)
    except ValueError:
        return False

    # Recalculate the signature using the server secret.
    expected_signature = hmac.new(
        SESSION_SECRET.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        submitted_signature,
        expected_signature,
    )


def set_csrf_cookie(response: Response, token: str):
    """Store the signed CSRF token in a browser cookie."""

    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def set_session_cookie(response: Response, token: str, expires_at: str):
    """Store the opaque session token in a secure browser cookie."""

    expiry = datetime.fromisoformat(expires_at)

    max_age = max(
        0,
        int((expiry - datetime.now(timezone.utc)).total_seconds()),
    )

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response):
    """Remove the session cookie from the browser."""

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


def clear_csrf_cookie(response: Response):
    """Remove the CSRF cookie from the browser."""

    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
