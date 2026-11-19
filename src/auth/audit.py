
import json

from src.database.connection import get_connection


def log_audit_event(
    event_type: str,
    user_id: int | None = None,
    details: dict | None = None,
):
    """Store a security event without sensitive credentials."""

    connection = get_connection()

    try:
        # Convert event details into JSON text.
        details_json = json.dumps(details or {})

        # Store the audit event in the database.
        connection.execute(
            """
            INSERT INTO audit_events (
                user_id,
                event_type,
                details
            )
            VALUES (?, ?, ?)
            """,
            (user_id, event_type, details_json),
        )

        connection.commit()

    finally:
        connection.close()
