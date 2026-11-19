
from src.auth.passwords import hash_password, verify_password


def test_password_is_hashed_using_argon2id():
    password = "MySecurePassphrase2026"

    password_hash = hash_password(password)

    assert password_hash.startswith("$argon2id$")
    assert password not in password_hash


def test_correct_password_is_verified():
    password = "MySecurePassphrase2026"

    password_hash = hash_password(password)

    assert verify_password(password, password_hash) is True


def test_wrong_password_is_rejected():
    password_hash = hash_password("MySecurePassphrase2026")

    assert verify_password("WrongPassword2026", password_hash) is False


def test_same_password_generates_different_hashes():
    password = "MySecurePassphrase2026"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash) is True
    assert verify_password(password, second_hash) is True
