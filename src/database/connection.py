
import sqlite3
from pathlib import Path


# Find the main project folder.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Store the authentication database inside the data folder.
DATABASE_PATH = BASE_DIR / "data" / "day16_auth.db"


def get_connection():
    """Create and return a SQLite database connection."""

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10,
    )

    # Return database rows that can be accessed by column name.
    connection.row_factory = sqlite3.Row

    # Enable foreign key validation.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
