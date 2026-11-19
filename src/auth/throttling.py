
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

from src.database.connection import get_connection


# Load the secret used to protect login identifiers.
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
)
load_dotenv(os.path.join(BASE_DIR, ".env"))

SESSION_SECRET = os.getenv("SESSION_SECRET")

if not SESSION_SECRET:
    raise RuntimeError("SESSION_SECRET is missing from the .env file")


# Login throttling settings.
MAX_FAILED_ATTEMPTS = 5
WINDOW_MINUTES = 15


def hash_identifier(email: str) -> str:
    """Create a protected identifier from the email address."""

    normalized_email = email.strip().lower()

    return hmac.new(
        SESSION_SECRET.encode("utf-8"),
        normalized_email.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def is_login_allowed(email: str) -> bool:
    """Check whether the email identifier can attempt login."""

    identifier_hash = hash_identifier(email)

    cutoff_time = (
        datetime.now(timezone.utc)
        - timedelta(minutes=WINDOW_MINUTES)
    ).strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()

    try:
        # Count recent failed attempts for this identifier.
        row = connection.execute(
            """
            SELECT COUNT(*) AS failure_count
            FROM login_attempts
            WHERE identifier_hash = ?
              AND failed_at > ?
            """,
            (identifier_hash, cutoff_time),
        ).fetchone()

        return row["failure_count"] < MAX_FAILED_ATTEMPTS

    finally:
        connection.close()


def record_failed_attempt(email: str):
    """Record a failed login attempt."""

    identifier_hash = hash_identifier(email)

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO login_attempts (identifier_hash)
            VALUES (?)
            """,
            (identifier_hash,),
        )

        connection.commit()

    finally:
        connection.close()


def clear_failed_attempts(email: str):
    """Clear failed attempts after a successful login."""

    identifier_hash = hash_identifier(email)

    connection = get_connection()

    try:
        connection.execute(
            """
            DELETE FROM login_attempts
            WHERE identifier_hash = ?
            """,
            (identifier_hash,),
        )

        connection.commit()

    finally:
        connection.close()
