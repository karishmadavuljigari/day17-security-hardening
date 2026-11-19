
import re
import uuid

import pytest

from fastapi.testclient import TestClient

from src.main import app, templates, UPLOAD_DIR
from src.database.connection import get_connection
from src.security import rate_limit

@pytest.fixture
def client():
    """Create an isolated browser-like test client."""

    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(autouse=True)
def clear_rate_limit_history():
    """Keep rate-limit history isolated between tests."""

    rate_limit.request_history.clear()

    yield

    rate_limit.request_history.clear()


def extract_csrf_token(response):
    """Extract the CSRF token from an HTML page."""

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        response.text,
    )

    assert match is not None, "CSRF token was not found"

    return match.group(1)


def register_and_login(client):
    """Register a test user and log in."""

    # Generate a unique email for each test.
    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "MySecureTestPassphrase2026"

    # Open the registration page.
    response = client.get("/register")
    assert response.status_code == 200

    token = extract_csrf_token(response)

    # Register the test user.
    response = client.post(
        "/register",
        data={
            "email": email,
            "password": password,
            "csrf_token": token,
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    # Open the login page.
    response = client.get("/login")
    assert response.status_code == 200

    token = extract_csrf_token(response)

    # Log in with the newly registered account.
    response = client.post(
        "/login",
        data={
            "email": email,
            "password": password,
            "csrf_token": token,
        },
    )

    assert response.status_code == 200
    assert email in response.text

    return email


def test_registration_page_loads(client):
    response = client.get("/register")

    assert response.status_code == 200
    assert "Register" in response.text
    assert 'name="csrf_token"' in response.text


def test_homepage_requires_login(client):
    response = client.get(
        "/",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_authenticated_homepage_loads(client):
    email = register_and_login(client)

    response = client.get("/")

    assert response.status_code == 200
    assert "Knowledge Assistant" in response.text
    assert email in response.text
    assert 'name="csrf_token"' in response.text


def test_valid_csrf_token_allows_question(client):
    register_and_login(client)

    # Open the homepage and get its CSRF token.
    response = client.get("/")
    token = extract_csrf_token(response)

    # Submit a question.
    response = client.post(
        "/ask",
        data={
            "question": "What is the leave policy?",
            "csrf_token": token,
        },
    )

    assert response.status_code == 200
    assert "What is the leave policy?" in response.text
    assert "Answer" in response.text
    assert "01_leave_policy.txt" in response.text


def test_invalid_csrf_token_is_rejected(client):
    register_and_login(client)

    response = client.post(
        "/ask",
        data={
            "question": "Test question",
            "csrf_token": "invalid-token",
        },
    )

    assert response.status_code == 403


def test_script_tag_is_escaped(client):
    register_and_login(client)

    response = client.get("/")
    token = extract_csrf_token(response)

    payload = '<script>alert("XSS")</script>'

    response = client.post(
        "/ask",
        data={
            "question": payload,
            "csrf_token": token,
        },
    )

    assert response.status_code == 200
    assert "&lt;script&gt;" in response.text
    assert "<script>" not in response.text


def test_css_file_loads(client):
    response = client.get("/static/css/style.css")

    assert response.status_code == 200
    assert ":focus-visible" in response.text


def test_security_headers_and_autoescaping(client):
    register_and_login(client)

    response = client.get("/")

    # Verify Content Security Policy.
    assert "Content-Security-Policy" in response.headers

    # Verify additional security headers.
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "Permissions-Policy" in response.headers

    # Verify HSTS is not enabled on local HTTP.
    assert "Strict-Transport-Security" not in response.headers

    # Verify Jinja2 autoescaping.
    assert templates.env.autoescape("answer.html") is True


def test_logout_invalidates_server_session(client):
    register_and_login(client)

    # Get a valid CSRF token from the homepage.
    response = client.get("/")
    token = extract_csrf_token(response)

    # Log out.
    response = client.post(
        "/logout",
        data={"csrf_token": token},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"

    # Try accessing the homepage after logout.
    response = client.get(
        "/",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_admin_endpoint_requires_login(client):
    response = client.get("/admin")

    assert response.status_code == 401


def test_employee_cannot_access_admin_endpoint(client):
    register_and_login(client)

    response = client.get("/admin")

    assert response.status_code == 403
    assert "Access denied" in response.text


def test_admin_can_access_admin_endpoint(client):
    email = register_and_login(client)

    # Promote this test account to admin in the test database.
    connection = get_connection()

    try:
        connection.execute(
            "UPDATE users SET role = 'admin' WHERE email = ?",
            (email,),
        )
        connection.commit()
    finally:
        connection.close()

    response = client.get("/admin")

    assert response.status_code == 200
    assert "Admin Dashboard" in response.text


def test_record_endpoint_requires_login(client):
    response = client.get("/records/1")

    assert response.status_code == 401


def test_users_can_only_access_their_own_records(client):
    # Register and log in as User A.
    email_a = register_and_login(client)

    connection = get_connection()

    try:
        user_a = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email_a,),
        ).fetchone()

        # Create a record owned by User A.
        cursor_a = connection.execute(
            """
            INSERT INTO records (owner_user_id, title, content)
            VALUES (?, ?, ?)
            """,
            (user_a["id"], "User A Record", "Private content A"),
        )

        record_a_id = cursor_a.lastrowid

        # Create a second test user directly in the database.
        email_b = f"other_{uuid.uuid4().hex}@example.com"

        cursor_b = connection.execute(
            """
            INSERT INTO users (email, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (email_b, "test_hash_not_used_for_login", "employee"),
        )

        user_b_id = cursor_b.lastrowid

        # Create a record owned by User B.
        cursor_b = connection.execute(
            """
            INSERT INTO records (owner_user_id, title, content)
            VALUES (?, ?, ?)
            """,
            (user_b_id, "User B Record", "Private content B"),
        )

        record_b_id = cursor_b.lastrowid

        connection.commit()

    finally:
        connection.close()

    # User A can access their own record.
    response = client.get(f"/records/{record_a_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "User A Record"

    # User A cannot access User B's record.
    response = client.get(f"/records/{record_b_id}")

    assert response.status_code == 404
    assert "Private content B" not in response.text

    # Log out User A.
    response = client.get("/")
    csrf_token = extract_csrf_token(response)

    client.post(
        "/logout",
        data={"csrf_token": csrf_token},
    )

    # Log in as User B using a fresh account session.
    response = client.get("/login")
    csrf_token = extract_csrf_token(response)

    # Set a known password for User B using the application hasher.
    from src.auth.passwords import hash_password

    connection = get_connection()

    try:
        connection.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (hash_password("AnotherSecurePassphrase2026"), email_b),
        )
        connection.commit()
    finally:
        connection.close()

    response = client.post(
        "/login",
        data={
            "email": email_b,
            "password": "AnotherSecurePassphrase2026",
            "csrf_token": csrf_token,
        },
    )

    assert response.status_code == 200

    # User B can access their own record.
    response = client.get(f"/records/{record_b_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "User B Record"


def test_session_cookie_security_flags(client):
    register_and_login(client)

    session_cookie = next(
        cookie
        for cookie in client.cookies.jar
        if cookie.name == "day16_session"
    )

    assert session_cookie.has_nonstandard_attr("HttpOnly")
    assert session_cookie.get_nonstandard_attr("SameSite").lower() == "lax"
    assert session_cookie.secure is False


def test_csrf_cookie_security_flags(client):
    client.get("/register")

    csrf_cookie = next(
        cookie
        for cookie in client.cookies.jar
        if cookie.name == "day16_csrf"
    )

    assert csrf_cookie.has_nonstandard_attr("HttpOnly")
    assert csrf_cookie.get_nonstandard_attr("SameSite").lower() == "lax"
    assert csrf_cookie.secure is False


def test_admin_can_only_access_their_own_records(client):
    """Admin role does not bypass record ownership."""

    # Register and log in as the first user.
    admin_email = register_and_login(client)

    connection = get_connection()

    try:
        admin = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (admin_email,),
        ).fetchone()

        # Promote the logged-in user to admin.
        connection.execute(
            "UPDATE users SET role = 'admin' WHERE id = ?",
            (admin["id"],),
        )

        # Create the admin's own record.
        own_cursor = connection.execute(
            """
            INSERT INTO records (owner_user_id, title, content)
            VALUES (?, ?, ?)
            """,
            (admin["id"], "Admin Own Record", "Admin private content"),
        )

        own_record_id = own_cursor.lastrowid

        # Create another user.
        other_email = f"other_admin_test_{uuid.uuid4().hex}@example.com"

        other_cursor = connection.execute(
            """
            INSERT INTO users (email, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (other_email, "unused_test_hash", "employee"),
        )

        other_user_id = other_cursor.lastrowid

        # Create a record owned by the other user.
        other_cursor = connection.execute(
            """
            INSERT INTO records (owner_user_id, title, content)
            VALUES (?, ?, ?)
            """,
            (other_user_id, "Other User Record", "Other private content"),
        )

        other_record_id = other_cursor.lastrowid

        connection.commit()

    finally:
        connection.close()

    # Admin can access their own record.
    response = client.get(f"/records/{own_record_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Admin Own Record"

    # Admin cannot access another user's record.
    response = client.get(f"/records/{other_record_id}")

    assert response.status_code == 404
    assert "Other private content" not in response.text

    # Admin also receives 404 for a nonexistent record.
    response = client.get("/records/999999999")

    assert response.status_code == 404


def test_cors_allows_trusted_origin(client):
    """Verify that a trusted origin is allowed by CORS."""

    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:8000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-csrf-token",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == (
        "http://localhost:8000"
    )
    assert response.headers["Access-Control-Allow-Credentials"] == "true"


def test_cors_rejects_untrusted_origin(client):
    """Verify that an untrusted origin is not allowed by CORS."""

    response = client.options(
        "/",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 400
    assert "Access-Control-Allow-Origin" not in response.headers


def test_ask_rate_limit_returns_429(client):
    """Verify that the sixth question is rate limited."""

    register_and_login(client)

    # Get a valid CSRF token.
    response = client.get("/")
    token = extract_csrf_token(response)

    # Submit five questions within the allowed limit.
    for _ in range(5):
        response = client.post(
            "/ask",
            data={
                "question": "What is the leave policy?",
                "csrf_token": token,
            },
        )

        assert response.status_code == 200

    # Submit a sixth question.
    response = client.post(
        "/ask",
        data={
            "question": "What is the leave policy?",
            "csrf_token": token,
        },
    )

    # Verify that the request is rejected.
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert "Too many requests" in response.text

def test_oversized_request_returns_413(client):
    """Verify that requests larger than 1 MB are rejected."""

    from src.main import MAX_REQUEST_SIZE

    # Create a request body that exceeds the configured limit.
    large_body = b"x" * (MAX_REQUEST_SIZE + 1)

    response = client.post(
        "/register",
        content=large_body,
    )

    assert response.status_code == 413
    assert "too large" in response.text.lower()
def test_authenticated_user_can_upload_text_file(client):
    """Verify that an authenticated user can upload a text file."""

    # Register and log in.
    register_and_login(client)

    # Get a valid CSRF token.
    response = client.get("/")
    token = extract_csrf_token(response)

    # Upload a plain text file.
    response = client.post(
        "/upload",
        data={"csrf_token": token},
        files={
            "file": (
                "my_notes.txt",
                b"This is a safe test file.",
                "text/plain",
            )
        },
    )

    # Verify successful upload.
    assert response.status_code == 200

    result = response.json()
    stored_filename = result["filename"]

    # Verify that the server generated a different filename.
    assert stored_filename != "my_notes.txt"
    assert stored_filename.endswith(".txt")

    # Verify that the file was saved with the correct content.
    saved_file = UPLOAD_DIR / stored_filename

    try:
        assert saved_file.exists()
        assert saved_file.read_bytes() == b"This is a safe test file."
    finally:
        # Remove the test file after verification.
        saved_file.unlink(missing_ok=True)

def test_unauthenticated_user_cannot_upload_file(client):
    """Verify that unauthenticated users cannot upload files."""

    response = client.post(
        "/upload",
        data={"csrf_token": "invalid-token"},
        files={
            "file": (
                "notes.txt",
                b"Test content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 401
    assert "Please log in" in response.text

def test_upload_rejects_invalid_csrf_token(client):
    """Verify that uploads require a valid CSRF token."""

    # Log in first.
    register_and_login(client)

    # Attempt upload with an invalid CSRF token.
    response = client.post(
        "/upload",
        data={"csrf_token": "invalid-token"},
        files={
            "file": (
                "notes.txt",
                b"Test content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 403
    assert "Invalid or expired security token" in response.text

def test_upload_rejects_unsupported_extension(client):
    """Verify that files with unsupported extensions are rejected."""

    # Log in and get a valid CSRF token.
    register_and_login(client)
    response = client.get("/")
    token = extract_csrf_token(response)

    # Try uploading a Python file instead of a text file.
    response = client.post(
        "/upload",
        data={"csrf_token": token},
        files={
            "file": (
                "script.py",
                b"print('Hello')",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Only .txt files are allowed" in response.text

def test_upload_rejects_invalid_content_type(client):
    """Verify that files with unsupported content types are rejected."""

    # Log in and get a valid CSRF token.
    register_and_login(client)
    response = client.get("/")
    token = extract_csrf_token(response)

    # Try uploading a .txt file with an unsupported content type.
    response = client.post(
        "/upload",
        data={"csrf_token": token},
        files={
            "file": (
                "notes.txt",
                b"Test content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert "Only plain text files are allowed" in response.text

def test_upload_rejects_oversized_file(client):
    """Verify that files larger than 512 KB are rejected."""

    # Log in and get a valid CSRF token.
    register_and_login(client)
    response = client.get("/")
    token = extract_csrf_token(response)

    # Create file content one byte larger than the limit.
    from src.main import MAX_UPLOAD_SIZE

    large_content = b"x" * (MAX_UPLOAD_SIZE + 1)

    # Attempt to upload the oversized file.
    response = client.post(
        "/upload",
        data={"csrf_token": token},
        files={
            "file": (
                "large.txt",
                large_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
    assert "File is too large" in response.text

def test_upload_rejects_binary_content(client):
    """Verify that binary content cannot be uploaded as a text file."""

    # Log in and get a valid CSRF token.
    register_and_login(client)
    response = client.get("/")
    token = extract_csrf_token(response)

    # Create content containing a null byte.
    binary_content = b"Hello\x00World"

    response = client.post(
        "/upload",
        data={"csrf_token": token},
        files={
            "file": (
                "binary.txt",
                binary_content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Binary content is not allowed" in response.text