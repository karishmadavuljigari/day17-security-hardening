# Day 16 — Secure Knowledge Assistant

A web-based Knowledge Assistant built using FastAPI, Jinja2, and HTMX, extended with secure user authentication, server-side sessions, role-based access control, and object-level ownership protection.

Users can register, log in, ask questions about company policies, and access only records they are authorized to view.

## Features

### Knowledge Assistant
- Retrieve information from 20 company policy documents.
- Display matching policy information and source filenames.
- Use HTMX to update answers without reloading the page.
- Handle empty and unsupported questions.

### Authentication and Password Security
- User registration and login.
- Argon2id password hashing.
- Minimum password length of 15 characters.
- Support for passwords of 64 characters or more.
- Local common-password blocklist validation.
- No character-composition requirements or forced periodic password rotation.

### Session and Request Security
- Server-side session management.
- Session token hashes stored in SQLite.
- Server-side session revocation on logout.
- HttpOnly, SameSite, and configurable Secure cookie flags.
- CSRF token validation.
- Login throttling after repeated failed attempts.

### Authorization and Audit
- Centralized employee/admin role-based access control.
- Admin-only endpoint protection.
- Object-level record ownership checks.
- Admins cannot bypass record ownership.
- IDOR attempt logging.
- Audit events for registration, login, logout, and denied access.

## Technology Stack

- Python 3.12
- FastAPI
- Uvicorn
- SQLite
- Jinja2
- HTMX
- Argon2id through pwdlib
- Python-dotenv
- Pytest
- HTTPX

## Project Structure

```text
day16_auth_project/
├── data/
│   ├── policy_docs/
│   ├── security/
│   │   └── common_passwords.txt
│   └── day16_auth.db
├── docs/
│   ├── day16_implementation_plan.md
│   ├── security_design_note.md
│   ├── access_control_test_matrix.md
│   ├── idor_attempt_log.md
│   ├── demo_storyline.md
│   ├── ai_use_log.md
│   └── screenshots/
├── src/
│   ├── auth/
│   ├── database/
│   ├── templates/
│   ├── main.py
│   └── retrieval.py
├── static/
│   ├── css/
│   └── js/
├── tests/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

The SQLite database is created locally during initialization and should not be committed to Git.

## Setup Instructions

### 1. Clone the repository

Replace the placeholder with the actual Day 16 repository URL after the repository has been published.

```bash
git clone YOUR_DAY16_REPOSITORY_URL
cd day16_auth_project
```

### 2. Create a virtual environment

```cmd
python -m venv .venv
```

### 3. Activate the virtual environment

Windows CMD:

```cmd
.venv\Scripts\activate
```

### 4. Install dependencies

```cmd
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root.

Generate a secure random session secret:

```cmd
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into `.env`:

```text
SESSION_SECRET=paste_your_generated_secret_here
COOKIE_SECURE=false
```

`COOKIE_SECURE=false` is for local HTTP development. Set it to `true` when deploying over HTTPS.

Never commit `.env` or share its secret value.

### 6. Initialize the database

```cmd
python -m src.database.init_db
```

Expected output:

```text
Database initialized successfully!
```

### 7. Start the application

```cmd
python -m uvicorn src.main:app --reload
```

Open the application:

http://127.0.0.1:8000

Register an account before logging in.

## Running Tests

Run the complete automated test suite:

```cmd
python -m pytest -v
```

### Latest Test Results

| Result | Count |
|---|---:|
| Passed | 46 |
| Failed | 0 |
| Skipped | 0 |

The suite covers password validation, Argon2id hashing, authentication, sessions, throttling, CSRF, cookie security, audit logging, RBAC, and record ownership.

One non-blocking Starlette deprecation warning was reported regarding the use of HTTPX with TestClient.

## Security Design

- **Password storage:** Argon2id hashing with unique salts.
- **Password validation:** Minimum 15 characters and local blocklist checking.
- **Sessions:** Opaque session tokens validated against server-side database records.
- **Cookies:** HttpOnly and SameSite=Lax, with Secure enabled for HTTPS deployment.
- **CSRF:** Signed double-submit cookie validation.
- **Login throttling:** Five failed attempts within a 15-minute window per email identifier.
- **RBAC:** Employee and admin roles.
- **Ownership:** Users can access only their own records, including admins.
- **Audit:** Security-relevant events are stored in the audit database.

## Known Limitations

- The local password blocklist is a small demonstration list, not a comprehensive breached-password database.
- Login throttling currently uses email-based identifiers; production should also consider IP-based or combined throttling.
- HTTPS and Secure cookies must be configured correctly for production.
- Password recovery and password changes following evidence of compromise require further implementation.
- Production deployment requires additional security hardening.

## Documentation

See the `docs/` directory for:

- Day 16 implementation plan.
- Security design note.
- Access-control test matrix.
- IDOR attempt log.
- Demo storyline.
- AI use log.

## License

This project was created as part of a learning assignment.