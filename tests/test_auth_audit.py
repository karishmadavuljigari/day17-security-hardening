
import uuid

from src.auth.users import register_user, authenticate_user
from src.auth.sessions import create_session, revoke_session
from src.database.connection import get_connection


def get_user_events(user_id):
    """Retrieve audit event types for a user."""

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT event_type
            FROM audit_events
            WHERE user_id = ?
            ORDER BY id
            """,
            (user_id,),
        ).fetchall()

        return [row["event_type"] for row in rows]

    finally:
        connection.close()


def test_registration_records_user_registered_event():
    email = f"audit_{uuid.uuid4().hex}@example.com"
    password = "MySecureAuditPassphrase2026"

    user_id = register_user(email, password)

    events = get_user_events(user_id)

    assert "USER_REGISTERED" in events


def test_failed_login_records_login_failure_event():
    email = f"audit_{uuid.uuid4().hex}@example.com"
    password = "MySecureAuditPassphrase2026"

    user_id = register_user(email, password)

    result = authenticate_user(email, "WrongPassword2026")

    assert result is None

    events = get_user_events(user_id)

    assert "LOGIN_FAILURE" in events


def test_successful_login_records_login_success_event():
    email = f"audit_{uuid.uuid4().hex}@example.com"
    password = "MySecureAuditPassphrase2026"

    user_id = register_user(email, password)

    result = authenticate_user(email, password)

    assert result is not None

    events = get_user_events(user_id)

    assert "LOGIN_SUCCESS" in events


def test_logout_records_logout_event():
    email = f"audit_{uuid.uuid4().hex}@example.com"
    password = "MySecureAuditPassphrase2026"

    user_id = register_user(email, password)

    session_token, expires_at = create_session(user_id)

    result = revoke_session(session_token)

    assert result is True

    events = get_user_events(user_id)

    assert "LOGOUT" in events
