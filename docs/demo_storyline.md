# Day 17 – FastAPI Security Hardening Demo

**Project:** FastAPI Security Hardening  
**GitHub:** https://github.com/karishmadavuljigari/day17-security-hardening  
**Duration:** 8–10 minutes

## 1. Introduction

"Today I am demonstrating the security hardening work completed on my FastAPI Knowledge Assistant application.

The objective was to improve application security through security headers, CORS restrictions, rate limiting, request-size protection, secure file uploads, dependency scanning, static analysis and secret detection."

## 2. Start the application

Run:

```cmd
python -m uvicorn src.main:app --reload
```

Open `http://127.0.0.1:8000`.

Explain that the application uses FastAPI and that security controls are implemented through middleware and endpoint validation.

## 3. Demonstrate security headers

Open another CMD window and run:

```cmd
curl.exe -I http://127.0.0.1:8000/
```

Explain these headers:

- Content-Security-Policy: restricts browser resource loading.
- X-Content-Type-Options: nosniff: prevents MIME-type sniffing.
- X-Frame-Options: DENY: prevents framing.
- Referrer-Policy: controls referrer information.
- Permissions-Policy: restricts browser features.

## 4. Demonstrate CORS

Open `src/main.py` and show the CORS configuration.

Explain that only the configured local origins, GET and POST methods, and required headers are allowed.

Configured origins:
- http://127.0.0.1:8000
- http://localhost:8000

## 5. Demonstrate rate limiting and request-size protection

Show:
- `src/security/rate_limit.py`
- The request-size middleware in `src/main.py`.

Explain:
- Rate limiting allows five requests per 60 seconds per client on `/ask`.
- Request bodies are limited to 1 MB.
- Oversized requests receive HTTP 413.

Show the corresponding tests.

## 6. Demonstrate secure file uploads

Open the upload endpoint in `src/main.py`.

Explain:
- Authentication and CSRF validation are required.
- Only `.txt` files with `text/plain` content type are accepted.
- Maximum upload size is 512 KB.
- UTF-8 validation and null-byte rejection are performed.
- The server generates a random filename rather than trusting the uploaded filename.

Show the upload tests in `tests/test_app.py`.

## 7. Demonstrate security scans

Open the reports under `docs/security/`.

Show:
- `pip_audit.txt`
- `bandit_report.txt`
- `semgrep_report.txt`

Explain the results:
- pip-audit: no known vulnerabilities after upgrading pip.
- Bandit: zero findings across 1,141 lines.
- Semgrep: zero findings across 19 files using 151 Python rules.
- pip check: no broken requirements.

## 8. Demonstrate AI code review and Gitleaks

Open `docs/security/ai_code_review.md`.

Explain that six insecure examples were reviewed:
- SQL injection
- Plaintext password storage
- Hardcoded secrets
- Missing CSRF validation
- Path traversal
- Insecure cookie settings

Then open `docs/security/leaked_secret_drill.md`.

Explain that a fake secret was committed in a separate temporary repository, detected by Gitleaks, followed by simulated rotation and Git history cleanup. The final scan verified the cleaned repository.

Do not display real credentials or private secret values.

## 9. Demonstrate automated tests

Stop the application if necessary and run:

```cmd
python -m pytest -v
```

Explain:

"The final test run completed with 60 passed and one non-blocking deprecation warning."

## 10. Conclusion

"I implemented multiple layers of security protection for the FastAPI application, reviewed dependencies, scanned the source code, reviewed insecure AI-generated examples and completed a secret-detection drill.

The automated tests passed, and the project was committed and pushed to GitHub."

GitHub repository:

https://github.com/karishmadavuljigari/day17-security-hardening

## Known limitations

- The request-size middleware uses Starlette's private `request._body` attribute, which needs compatibility review during future upgrades.
- One non-blocking Starlette/httpx deprecation warning remains.
- Local development CORS origins and cookie settings need production review.
- The common-password blocklist should be expanded for production use.