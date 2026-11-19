
import uuid
from src.auth.users import register_user, authenticate_user

from src.auth.throttling import (
    hash_identifier,
    is_login_allowed,
    record_failed_attempt,
    clear_failed_attempts,
    MAX_FAILED_ATTEMPTS,
)


def test_email_identifier_is_hashed():
    email = f"test_{uuid.uuid4().hex}@example.com"

    identifier_hash = hash_identifier(email)

    assert identifier_hash != email
    assert len(identifier_hash) == 64


def test_email_hash_is_case_insensitive():
    email = f"test_{uuid.uuid4().hex}@example.com"

    assert hash_identifier(email) == hash_identifier(email.upper())


def test_login_is_blocked_after_five_failed_attempts():
    email = f"test_{uuid.uuid4().hex}@example.com"

    assert is_login_allowed(email) is True

    for _ in range(MAX_FAILED_ATTEMPTS):
        record_failed_attempt(email)

    assert is_login_allowed(email) is False


def test_successful_login_clears_failed_attempts():
    email = f"test_{uuid.uuid4().hex}@example.com"

    for _ in range(MAX_FAILED_ATTEMPTS):
        record_failed_attempt(email)

    assert is_login_allowed(email) is False

    clear_failed_attempts(email)

    assert is_login_allowed(email) is True


def test_authentication_is_blocked_after_five_failed_attempts():
    email = f"blocked_{uuid.uuid4().hex}@example.com"
    password = "MySecureThrottlePassphrase2026"

    register_user(email, password)

    for _ in range(MAX_FAILED_ATTEMPTS):
        assert authenticate_user(email, "WrongPassword2026") is None

    # Even the correct password must be blocked now.
    assert authenticate_user(email, password) is None


def test_successful_authentication_clears_failed_attempts():
    email = f"clear_{uuid.uuid4().hex}@example.com"
    password = "MySecureThrottlePassphrase2026"

    register_user(email, password)

    # Create some failed attempts.
    for _ in range(3):
        assert authenticate_user(email, "WrongPassword2026") is None

    # Correct credentials should still work.
    result = authenticate_user(email, password)

    assert result is not None
    assert result["email"] == email
    assert is_login_allowed(email) is True
