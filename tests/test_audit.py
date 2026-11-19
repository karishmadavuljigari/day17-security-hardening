
from src.auth.audit import log_audit_event
from src.database.connection import get_connection


def test_audit_event_is_saved():
    """Verify that an audit event is stored correctly."""

    log_audit_event(
        event_type="TEST_LOGIN_SUCCESS",
        user_id=1,
        details={"method": "password"},
    )

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT event_type, user_id, details
            FROM audit_events
            WHERE event_type = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            ("TEST_LOGIN_SUCCESS",),
        ).fetchone()

        assert row is not None
        assert row["event_type"] == "TEST_LOGIN_SUCCESS"
        assert row["user_id"] == 1
        assert '"method": "password"' in row["details"]

    finally:
        connection.close()


def test_audit_event_without_user():
    """Verify that events can be recorded without a user account."""

    log_audit_event(
        event_type="TEST_LOGIN_FAILURE",
        user_id=None,
        details={"reason": "unknown_email"},
    )

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT event_type, user_id
            FROM audit_events
            WHERE event_type = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            ("TEST_LOGIN_FAILURE",),
        ).fetchone()

        assert row is not None
        assert row["event_type"] == "TEST_LOGIN_FAILURE"
        assert row["user_id"] is None

    finally:
        connection.close()
