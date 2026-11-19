
from src.database.connection import get_connection
from src.auth.audit import log_audit_event


def get_owned_record(record_id: int, user: dict):
    """Return a record only if it belongs to the current user."""

    connection = get_connection()

    try:
        # Find the record only when the current user owns it.
        record = connection.execute(
            """
            SELECT id, owner_user_id, title, content
            FROM records
            WHERE id = ?
              AND owner_user_id = ?
            """,
            (record_id, user["id"]),
        ).fetchone()

        if record is None:
            # Record the denied ownership access.
            log_audit_event(
                event_type="IDOR_ATTEMPT",
                user_id=user["id"],
                details={"record_id": record_id},
            )

            return None

        return dict(record)

    finally:
        connection.close()
