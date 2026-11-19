
from src.auth.password_validation import validate_password


def test_password_shorter_than_15_characters_is_rejected():
    valid, message = validate_password("Short123!")

    assert valid is False
    assert "15 characters" in message


def test_password_with_exactly_15_characters_is_accepted():
    valid, message = validate_password("abcdefghijklmno")

    assert valid is True


def test_password_with_64_characters_is_accepted():
    valid, message = validate_password("A" * 64)

    assert valid is True


def test_password_with_100_characters_is_accepted():
    valid, message = validate_password("A" * 100)

    assert valid is True


def test_blocklisted_password_is_rejected():
    valid, message = validate_password("passwordpassword")

    assert valid is False
    assert "commonly used" in message


def test_blocklist_check_is_case_insensitive():
    valid, message = validate_password("PASSWORDPASSWORD")

    assert valid is False


def test_password_does_not_require_special_characters():
    valid, message = validate_password("this is a valid long passphrase")

    assert valid is True


def test_password_longer_than_maximum_is_rejected():
    valid, message = validate_password("A" * 1025)

    assert valid is False
    assert "too long" in message
