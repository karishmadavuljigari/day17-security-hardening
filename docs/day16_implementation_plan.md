\# Day 16 — Authentication Project Implementation Plan



\## 1. Objective



Extend the existing Knowledge Assistant with secure user registration, authentication, session management, login throttling, role-based access control, object-level ownership checks, and security audit logging.



Preserve the existing policy retrieval functionality.



\## 2. Requirements



\### Authentication and Password Security

\- Implement user registration and login.

\- Hash passwords using Argon2id.

\- Require a minimum password length of 15 characters.

\- Accept passwords of 64 characters or more.

\- Reject passwords found in a password blocklist.

\- Do not enforce character-composition rules.

\- Do not force periodic password changes.

\- Require password changes when compromise is established.



\### Session and Request Security

\- Use server-side sessions.

\- Store session token hashes in the database.

\- Configure HttpOnly, Secure, and SameSite cookie flags.

\- Revoke sessions on logout.

\- Implement CSRF protection.

\- Apply login throttling.



\### Authorization

\- Implement centralized employee/admin RBAC.

\- Protect the admin endpoint.

\- Enforce object-level record ownership.

\- Do not allow admin privileges to bypass record ownership.

\- Prevent IDOR vulnerabilities.



\### Audit Logging

\- Record registration, successful login, failed login, and logout events.

\- Record access-denied and IDOR-related events.

\- Never log passwords, password hashes, or session secrets.



\## 3. Implementation Approach



\### Phase 1: Project Setup

\- Create a separate Day 16 project.

\- Configure the Python virtual environment.

\- Install required dependencies.

\- Configure environment variables.

\- Initialize the SQLite database.



\### Phase 2: Password Security

\- Implement Argon2id hashing and verification.

\- Implement password validation.

\- Add a local password blocklist.

\- Test password length and blocklist requirements.



\### Phase 3: Authentication and Sessions

\- Implement registration and login.

\- Implement server-side session creation and validation.

\- Configure session cookies.

\- Implement logout and server-side session revocation.

\- Add CSRF protection.



\### Phase 4: Login Protection and Audit

\- Implement failed-login throttling.

\- Store hashed login identifiers.

\- Record authentication and security events.

\- Test audit event generation.



\### Phase 5: Authorization

\- Implement centralized RBAC.

\- Protect admin-only endpoints.

\- Implement record ownership checks.

\- Log denied access and IDOR attempts.

\- Verify that admins cannot access records owned by other users.



\### Phase 6: Testing

\- Test password validation and hashing.

\- Test registration and authentication.

\- Test session expiry and logout invalidation.

\- Test cookie security flags and CSRF protection.

\- Test login throttling.

\- Test employee/admin permissions.

\- Test own-record and other-user-record access.

\- Verify audit events.



\### Phase 7: Documentation and Delivery

\- Prepare the security design note.

\- Prepare the access-control test matrix.

\- Document IDOR audit evidence.

\- Prepare the demo storyline.

\- Maintain the AI use log.

\- Update the project README.

\- Verify clean-clone setup instructions.



\## 4. Acceptance Criteria



\- Passwords are stored using Argon2id hashes.

\- Password validation follows the specified NIST-aligned rules.

\- Login throttling blocks repeated failed attempts.

\- Session cookies have the required security flags.

\- Logout invalidates the server-side session.

\- CSRF-protected requests reject invalid tokens.

\- Employees cannot access admin-only functionality.

\- Users cannot access another user's private records.

\- Admins cannot bypass record ownership.

\- Security events are recorded without exposing secrets.

\- Automated tests pass.

\- Existing policy retrieval functionality remains operational.

\- Project setup instructions work from a clean clone.



\## 5. Known Limitations



\- The current local password blocklist is a demonstration list.

\- Login throttling currently uses an email identifier and should be extended for production.

\- Secure cookies must be enabled for HTTPS deployment.

\- Production deployment requires additional security and operational hardening.



\## 6. Implementation Status



The authentication, session, password validation, throttling, audit, RBAC, and ownership components have been implemented.



Application tests currently pass, including employee and admin ownership checks. Final full-suite verification and clean-clone verification remain part of delivery.
