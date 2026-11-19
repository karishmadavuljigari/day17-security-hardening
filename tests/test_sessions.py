
from src.auth.sessions import (
    create_session,
    get_session_user,
    revoke_session,
)
from uuid import uuid4
from src.auth.users import register_user


def test_session_creation_and_validation():
    """A newly created session should identify its user."""

    email = f"test_{uuid4().hex}@example.com"
    password = "Secure-Test-Password-2026!"

    user_id = register_user(email, password)

    token, expiry = create_session(user_id)

    assert token
    assert expiry
    assert get_session_user(token) == {
        "id": user_id,
        "email": email,
        "role": "employee",
    }


def test_revoked_session_is_rejected():
    """A revoked session must no longer be accepted."""

    token, expiry = create_session(1)

    assert get_session_user(token) is not None

    assert revoke_session(token) is True

    assert get_session_user(token) is None


def test_unknown_session_is_rejected():
    """An unknown token must not identify a user."""

    assert get_session_user("unknown-session-token") is None


import hashlib
from datetime import datetime, timedelta, timezone

from src.database.connection import get_connection


def test_database_stores_only_session_token_hash():
    """The original session token must never be stored in the database."""

    token, expiry = create_session(1)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT token_hash
            FROM sessions
            WHERE token_hash = ?
            """,
            (token_hash,),
        ).fetchone()

        assert row is not None
        assert row["token_hash"] == token_hash
        assert row["token_hash"] != token

    finally:
        connection.close()


def test_expired_session_is_rejected():
    """An expired session must not identify a user."""

    token, expiry = create_session(1)

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    expired_time = (
        datetime.now(timezone.utc) - timedelta(hours=1)
    ).isoformat()

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE sessions
            SET expires_at = ?
            WHERE token_hash = ?
            """,
            (expired_time, token_hash),
        )

        connection.commit()

    finally:
        connection.close()

    assert get_session_user(token) is None
