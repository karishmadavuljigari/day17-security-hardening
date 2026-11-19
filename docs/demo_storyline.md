\# Day 16 Authentication Project — Demo Storyline



\## 1. Introduction



This project extends the Knowledge Assistant with secure user registration, authentication, session management, role-based access control, and record ownership protection.



The goal is to protect user accounts and private records while retaining the existing policy retrieval functionality.



\## 2. Demo Sequence



\### Step 1: Register a User



\- Open `/register`.

\- Register with a valid email and a password of at least 15 characters.

\- Explain that passwords are validated against a local blocklist.

\- Explain that passwords are stored as Argon2id hashes, never as plaintext.



\### Step 2: Demonstrate Password Validation



Explain the implemented password rules:



\- Minimum 15 characters.

\- Accept passwords of 64 characters or more.

\- Reject passwords found in the local blocklist.

\- No mandatory uppercase, lowercase, digit, or special-character composition rules.

\- No forced periodic password rotation.



Mention that the current blocklist is a small demonstration list and should be expanded for production.



\### Step 3: Log In



\- Log in with the registered credentials.

\- Show that successful authentication creates a server-side session.

\- Explain that the browser receives an opaque session cookie.

\- Explain the HttpOnly, SameSite, and Secure cookie settings.



\### Step 4: Demonstrate Protected Knowledge Assistant



\- Open the homepage while logged in.

\- Submit a policy-related question.

\- Show that the existing policy retrieval functionality still works.

\- Explain that unauthenticated users are redirected to the login page.



\### Step 5: Demonstrate Login Protection



\- Explain the login throttling rule: five failed attempts within 15 minutes.

\- Explain that failed attempts are tracked using a hashed email identifier.

\- Show the relevant automated tests rather than repeatedly locking a real account.



\### Step 6: Demonstrate RBAC



\- Access `/admin` as an employee.

\- Show that access is denied with HTTP 403.

\- Explain that only users with the admin role can access the admin endpoint.

\- Explain that denied access is recorded as `ACCESS\_DENIED`.



\### Step 7: Demonstrate Object-Level Ownership



\- Create or use two separate user accounts.

\- Show that each user can access their own record.

\- Attempt to access the other user's record.

\- Show HTTP 404 and confirm that private record content is not returned.

\- Explain that admins cannot bypass record ownership checks.



\### Step 8: Demonstrate Audit Logging



Explain that the audit system records registration, login success, login failure, logout, access denial, and IDOR-related events.



Show the audit event counts and the IDOR attempt log.



\### Step 9: Demonstrate Logout



\- Submit the logout form.

\- Explain that the server-side session is revoked.

\- Show that the browser cookies are cleared.

\- Attempt to revisit the protected homepage.

\- Show that the user must log in again.



\## 3. Testing Evidence



Run the complete automated test suite:



```cmd

python -m pytest -v

```



Show the final test summary and explain that the tests cover password validation, authentication, session invalidation, throttling, CSRF, audit logging, RBAC, and ownership checks.



\## 4. Closing Summary



The project demonstrates a layered authentication and authorization design:



\- Argon2id password hashing.

\- NIST-aligned password validation.

\- Server-side session management.

\- Secure cookie settings and CSRF protection.

\- Login throttling.

\- Centralized role-based authorization.

\- Object-level ownership enforcement.

\- Security audit logging.

\- Automated security tests.



\## 5. Known Limitations



\- The local password blocklist is a demonstration list, not a comprehensive breached-password database.

\- Login throttling currently uses an email identifier; production should also consider IP-based or combined throttling.

\- Secure cookies must be enabled when deployed over HTTPS.

\- Production deployment requires additional operational hardening.
