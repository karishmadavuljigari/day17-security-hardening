
from src.database.connection import get_connection
from src.auth.passwords import hash_password, verify_password
from src.auth.password_validation import validate_password
from src.auth.audit import log_audit_event
from src.auth.throttling import (
    is_login_allowed,
    record_failed_attempt,
    clear_failed_attempts,
)


def register_user(email: str, password: str) -> int:
    """Validate and register a new user."""

    # Validate the password before hashing it.
    is_valid, message = validate_password(password)

    if not is_valid:
        raise ValueError(message)

    # Hash the password using Argon2id.
    password_hash = hash_password(password)

    # Store the user account in the database.
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
            """,
            (email.strip().lower(), password_hash),
        )

        connection.commit()

        user_id = cursor.lastrowid

    finally:
        connection.close()

    # Record the successful registration.
    log_audit_event(
        event_type="USER_REGISTERED",
        user_id=user_id,
    )

    return user_id


def authenticate_user(email: str, password: str):
    """Authenticate a user using email and password."""

    # Check whether this email is temporarily blocked.
    if not is_login_allowed(email):
        log_audit_event(
            event_type="LOGIN_FAILURE",
            details={"reason": "login_throttled"},
        )
        return None

    connection = get_connection()

    try:
        # Find the registered user by email.
        user = connection.execute(
            """
            SELECT id, email, password_hash, role
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()

        # Reject if the account does not exist.
        if user is None:
            record_failed_attempt(email)

            log_audit_event(
                event_type="LOGIN_FAILURE",
                details={"reason": "unknown_email"},
            )
            return None

        # Verify the entered password against the stored hash.
        if not verify_password(password, user["password_hash"]):
            record_failed_attempt(email)

            log_audit_event(
                event_type="LOGIN_FAILURE",
                user_id=user["id"],
                details={"reason": "incorrect_password"},
            )
            return None

        # Return user details without exposing the password hash.
        authenticated_user = {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
        }

    finally:
        connection.close()

    # Clear previous failed attempts after successful login.
    clear_failed_attempts(email)

    # Record the successful login.
    log_audit_event(
        event_type="LOGIN_SUCCESS",
        user_id=authenticated_user["id"],
    )

    return authenticated_user
