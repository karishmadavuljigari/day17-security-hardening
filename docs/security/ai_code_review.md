\# Day 17 – AI-Generated Code Security Review



\## Objective



Review six AI-generated code snippets containing intentionally planted security flaws.



The purpose is to identify insecure code, understand the risk, and provide corrective review comments before accepting AI-generated code.



\*\*Important:\*\* These snippets are for security review only. They must not be added to the working application or executed.



\---



\## 1. SQL Injection



\### AI-generated snippet



```python

def get\_user(username):

&#x20;   connection = sqlite3.connect("app.db")

&#x20;   query = f"SELECT \* FROM users WHERE username = '{username}'"

&#x20;   return connection.execute(query).fetchone()

```



\### Reviewer comment



\*\*Finding:\*\* SQL injection vulnerability.



\*\*Problem:\*\* The username is directly inserted into the SQL query using an f-string. An attacker could provide specially crafted input to change the meaning of the SQL statement.



\*\*Impact:\*\* Unauthorized database access, data disclosure, or modification.



\*\*Recommended correction:\*\* Use parameterized SQL queries.



```python

query = "SELECT \* FROM users WHERE username = ?"

return connection.execute(query, (username,)).fetchone()

```



\*\*Decision:\*\* Reject the original snippet. Accept only after parameterized queries are used.



\---



\## 2. Plaintext Password Storage



\### AI-generated snippet



```python

def register\_user(username, password):

&#x20;   connection = sqlite3.connect("app.db")

&#x20;   connection.execute(

&#x20;       "INSERT INTO users (username, password) VALUES (?, ?)",

&#x20;       (username, password)

&#x20;   )

&#x20;   connection.commit()

```



\### Reviewer comment



\*\*Finding:\*\* Passwords are stored in plaintext.



\*\*Problem:\*\* The password is saved directly in the database without secure password hashing.



\*\*Impact:\*\* If the database is exposed, attackers can immediately read users' passwords.



\*\*Recommended correction:\*\* Use a dedicated password-hashing algorithm such as Argon2id with a unique salt. Verify passwords using the password-hashing library.



\*\*Decision:\*\* Reject the original snippet. Use the application's existing Argon2id password-hashing approach.



\---



\## 3. Hardcoded Secret Key



\### AI-generated snippet



```python

SESSION\_SECRET = "my-super-secret-key-123"



def create\_session(data):

&#x20;   serializer = URLSafeSerializer(SESSION\_SECRET)

&#x20;   return serializer.dumps(data)

```



\### Reviewer comment



\*\*Finding:\*\* Hardcoded application secret.



\*\*Problem:\*\* The secret is written directly in the source code.



\*\*Impact:\*\* Anyone who obtains the source code may be able to forge or manipulate signed session data.



\*\*Recommended correction:\*\* Load a strong, randomly generated secret from an environment variable. Keep `.env` out of Git and never commit actual secret values.



\*\*Decision:\*\* Reject the original snippet. Use the existing environment-based session secret configuration.



\---



\## 4. Missing CSRF Validation



\### AI-generated snippet



```python

@app.post("/change-email")

async def change\_email(request: Request, email: str = Form(...)):

&#x20;   user = get\_current\_user(request)



&#x20;   if user is None:

&#x20;       return HTMLResponse("Please log in.", status\_code=401)



&#x20;   update\_email(user\["id"], email)



&#x20;   return {"message": "Email updated"}

```



\### Reviewer comment



\*\*Finding:\*\* Missing Cross-Site Request Forgery (CSRF) protection.



\*\*Problem:\*\* The endpoint checks whether the user is logged in but does not validate a CSRF token.



\*\*Impact:\*\* An attacker may trick an authenticated user's browser into submitting an unwanted request.



\*\*Recommended correction:\*\* Validate a CSRF token against the expected session or cookie token before performing the state-changing operation. Keep authentication and authorization checks as well.



\*\*Decision:\*\* Reject the original snippet. Add CSRF validation before updating the email.



\---



\## 5. File Upload Path Traversal



\### AI-generated snippet



```python

@app.post("/upload")

async def upload(file: UploadFile = File(...)):

&#x20;   destination = Path("uploads") / file.filename



&#x20;   content = await file.read()

&#x20;   destination.write\_bytes(content)



&#x20;   return {"message": "Uploaded"}

```



\### Reviewer comment



\*\*Finding:\*\* Unsafe use of the client-provided filename.



\*\*Problem:\*\* The filename comes from the user and is used directly to construct a filesystem path. A malicious filename containing path traversal components may target locations outside the intended upload directory.



\*\*Impact:\*\* Unauthorized file overwriting or writing outside the upload directory.



\*\*Recommended correction:\*\* Generate a random server-side filename, validate allowed file types and content, enforce a file-size limit, and ensure files are stored in a controlled directory.



\*\*Decision:\*\* Reject the original snippet. Use the application's UUID-based filename and upload validation approach.



\---



\## 6. Insecure Session Cookie Settings



\### AI-generated snippet



```python

response.set\_cookie(

&#x20;   key="session",

&#x20;   value=session\_token,

&#x20;   httponly=False,

&#x20;   secure=False,

&#x20;   samesite="none"

)

```



\### Reviewer comment



\*\*Finding:\*\* Insecure session cookie configuration.



\*\*Problem:\*\*

\- `httponly=False` allows JavaScript to access the cookie.

\- `secure=False` allows the cookie to be transmitted over unencrypted HTTP.

\- `samesite="none"` permits cross-site cookie sending and requires the Secure attribute in modern browsers.



\*\*Impact:\*\* Increased risk of session theft through client-side script attacks or insecure network transmission.



\*\*Recommended correction:\*\* Set `httponly=True`, `secure=True` in HTTPS production environments, and an appropriate SameSite policy such as `lax`. Configure cookie lifetime and scope appropriately.



\*\*Decision:\*\* Reject the original snippet. Use secure cookie settings appropriate to the deployment environment.



\---



\## Overall Review Summary



| No. | Security flaw | Severity assessment | Review decision |

|---|---|---|---|

| 1 | SQL injection | High | Reject; parameterize SQL |

| 2 | Plaintext password storage | Critical | Reject; use Argon2id |

| 3 | Hardcoded secret | High | Reject; use environment configuration |

| 4 | Missing CSRF validation | High | Reject; validate CSRF token |

| 5 | File upload path traversal | High | Reject; generate server-side filename |

| 6 | Insecure session cookies | High | Reject; use secure cookie attributes |



\## General AI Code Review Rules



Before accepting AI-generated code:



1\. Check how user input is handled.

2\. Check database queries for parameterization.

3\. Never store plaintext passwords or hardcode secrets.

4\. Validate authentication, authorization, and CSRF protection.

5\. Validate uploaded files and restrict filesystem access.

6\. Configure cookies and security headers safely.

7\. Run automated tests and security scanners after changes.



\*\*Conclusion:\*\* All six intentionally flawed snippets were reviewed. Security risks, potential impacts, and recommended corrections were documented. None of the insecure examples were added to the working application.
