
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from src.database.connection import get_connection
from src.auth.audit import log_audit_event


# Session lifetime: 8 hours.
SESSION_DURATION_HOURS = 8


def create_session(user_id: int) -> tuple[str, str]:
    """Create a new server-side session for a user."""

    # Generate a secure random session token.
    session_token = secrets.token_urlsafe(32)

    # Hash the token before storing it in the database.
    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    # Calculate the session expiry time.
    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(hours=SESSION_DURATION_HOURS)
    ).isoformat()

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO sessions (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
            """,
            (user_id, token_hash, expires_at),
        )

        connection.commit()

    finally:
        connection.close()

    # Return the original token and expiry time to the application.
    return session_token, expires_at


def get_session_user(session_token: str):
    """Return the user if the session token is valid."""

    # Reject an empty session token.
    if not session_token:
        return None

    # Hash the token to compare it with the database value.
    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    try:
        # Find an active session belonging to a registered user.
        session = connection.execute(
            """
            SELECT
                users.id,
                users.email,
                users.role,
                sessions.expires_at
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ?
              AND sessions.revoked_at IS NULL
            """,
            (token_hash,),
        ).fetchone()

        # Reject tokens that do not exist or have been revoked.
        if session is None:
            return None

        # Check whether the session has expired.
        expires_at = datetime.fromisoformat(session["expires_at"])

        if expires_at <= datetime.now(timezone.utc):
            return None

        # Return user details without exposing session data.
        return {
            "id": session["id"],
            "email": session["email"],
            "role": session["role"],
        }

    finally:
        connection.close()



def revoke_session(session_token: str) -> bool:
    """Invalidate a session on the server."""

    if not session_token:
        return False

    # Hash the original token to find its database record.
    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    try:
        # Find the user who owns this active session.
        session = connection.execute(
            """
            SELECT user_id
            FROM sessions
            WHERE token_hash = ?
              AND revoked_at IS NULL
            """,
            (token_hash,),
        ).fetchone()

        if session is None:
            return False

        # Mark the session as revoked.
        connection.execute(
            """
            UPDATE sessions
            SET revoked_at = ?
            WHERE token_hash = ?
              AND revoked_at IS NULL
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                token_hash,
            ),
        )

        connection.commit()

        user_id = session["user_id"]

    finally:
        connection.close()

    # Record the successful logout.
    log_audit_event(
        event_type="LOGOUT",
        user_id=user_id,
    )

    return True
