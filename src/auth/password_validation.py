
from pathlib import Path


# Find the main project folder.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Minimum password length when password is the only authentication factor.
MIN_PASSWORD_LENGTH = 15

# Maximum accepted password length.
MAX_PASSWORD_LENGTH = 1024

# Find the local password blocklist file.
BLOCKLIST_PATH = BASE_DIR / "data" / "security" / "common_passwords.txt"


def load_blocklist() -> set[str]:
    """Load commonly used passwords from the local blocklist file."""

    if not BLOCKLIST_PATH.exists():
        raise FileNotFoundError(
            f"Password blocklist not found: {BLOCKLIST_PATH}"
        )

    with BLOCKLIST_PATH.open("r", encoding="utf-8") as file:
        return {
            line.strip().casefold()
            for line in file
            if line.strip()
        }


# Load the blocklist when this module is imported.
BLOCKLIST = load_blocklist()


def validate_password(password: str) -> tuple[bool, str]:
    """Validate a password using the project's NIST requirements."""

    # Check the minimum password length.
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, "Password must contain at least 15 characters."

    # Check the maximum accepted password length.
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, "Password is too long."

    # Check whether the password appears in the blocklist.
    if password.casefold() in BLOCKLIST:
        return False, "This password is commonly used. Choose another one."

    return True, "Password is valid."
