
from src.database.connection import get_connection


def initialize_database():
    """Create all authentication database tables."""

    connection = get_connection()

    # 1. Store registered users.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee'
                CHECK (role IN ('employee', 'admin')),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Store server-side sessions.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            csrf_token TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            revoked_at TEXT,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)
    # Add the CSRF token column to existing session tables.
    session_columns = connection.execute(
        "PRAGMA table_info(sessions)"
    ).fetchall()

    if "csrf_token" not in [
        column["name"] for column in session_columns
    ]:
        connection.execute(
            "ALTER TABLE sessions ADD COLUMN csrf_token TEXT"
        )

    # 3. Store security audit events.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    # 4. Store user-owned records.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    # 5. Track failed login attempts.
    connection.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier_hash TEXT NOT NULL,
            failed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create indexes for faster lookups.
    connection.execute("""
        CREATE INDEX IF NOT EXISTS sessions_user_idx
        ON sessions(user_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS records_owner_idx
        ON records(owner_user_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS audit_user_idx
        ON audit_events(user_id)
    """)

    connection.execute("""
        CREATE INDEX IF NOT EXISTS login_identifier_idx
        ON login_attempts(identifier_hash, failed_at)
    """)

    connection.commit()
    connection.close()
