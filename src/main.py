import os
import hmac
import sqlite3
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.retrieval import search_policies
from src.security.rate_limit import check_rate_limit
from src.auth.users import register_user, authenticate_user
from src.auth.sessions import create_session, revoke_session
from src.auth.permissions import require_role
from src.auth.ownership import get_owned_record
from src.auth.web import (
    SESSION_COOKIE_NAME,
    CSRF_COOKIE_NAME,
    get_current_user,
    create_csrf_token,
    validate_csrf_token,
    set_csrf_cookie,
    set_session_cookie,
    clear_session_cookie,
    clear_csrf_cookie,
)


# Find the main project folder.
BASE_DIR = Path(__file__).resolve().parent.parent
# Configure safe file upload restrictions.
UPLOAD_DIR = BASE_DIR / "uploads"
MAX_UPLOAD_SIZE = 512 * 1024
ALLOWED_CONTENT_TYPES = {"text/plain"}
load_dotenv(BASE_DIR / ".env")


# Configure Jinja2 templates.
templates = Jinja2Templates(
    directory=str(BASE_DIR / "src" / "templates")
)

# Create the FastAPI application.
app = FastAPI()
# Allow requests only from trusted local development origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

# Serve CSS and other static files.
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


# Add Content-Security-Policy security header.


# Maximum allowed request body size: 1 MB.
MAX_REQUEST_SIZE = 1_048_576


# Reject requests whose body exceeds the size limit.
@app.middleware("http")
async def limit_request_size(request: Request, call_next):

    # Check the declared request size, if available.
    content_length = request.headers.get("content-length")

    if content_length is not None:
        try:
            if int(content_length) > MAX_REQUEST_SIZE:
                return HTMLResponse(
                    "Request body is too large.",
                    status_code=413,
                )
        except ValueError:
            return HTMLResponse(
                "Invalid Content-Length header.",
                status_code=400,
            )

    # Read the request body in chunks and enforce the limit.
    body = bytearray()

    async for chunk in request.stream():
        if len(body) + len(chunk) > MAX_REQUEST_SIZE:
            return HTMLResponse(
                "Request body is too large.",
                status_code=413,
            )

        body.extend(chunk)

    # Cache the accepted body so the endpoint can read it normally.
    request._body = bytes(body)

    return await call_next(request)

# Add security headers to every HTTP response.
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Restrict where browser resources can load from.
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://unpkg.com; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "form-action 'self'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'; "
        "object-src 'none'"
    )

    # Prevent browsers from guessing file content types.
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent the application from being embedded in frames.
    response.headers["X-Frame-Options"] = "DENY"

    # Control how much referrer information is shared.
    response.headers["Referrer-Policy"] = (
        "strict-origin-when-cross-origin"
    )

    # Disable browser features that this application does not need.
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    return response



# Display the registration page.
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):

    csrf_token = create_csrf_token()

    response = templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
            "csrf_token": csrf_token,
            "error": None,
        },
    )

    set_csrf_cookie(response, csrf_token)

    return response


# Receive and validate a new user registration.
@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

    if not validate_csrf_token(csrf_token, cookie_token):
        return HTMLResponse(
            "Invalid or expired security token. Refresh the page.",
            status_code=403,
        )

    try:
        register_user(email, password)

    except ValueError as error:
        message = str(error)

    except sqlite3.IntegrityError:
        message = "An account with this email already exists."

    else:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    # Generate a fresh CSRF token when showing the error.
    new_csrf_token = create_csrf_token()

    response = templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
            "csrf_token": new_csrf_token,
            "error": message,
        },
        status_code=400,
    )

    set_csrf_cookie(response, new_csrf_token)

    return response


# Display the login page.
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    csrf_token = create_csrf_token()

    response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "csrf_token": csrf_token,
            "error": None,
        },
    )

    set_csrf_cookie(response, csrf_token)

    return response


# Authenticate a user and create a server-side session.
@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
):

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

    if not validate_csrf_token(csrf_token, cookie_token):
        return HTMLResponse(
            "Invalid or expired security token. Refresh the page.",
            status_code=403,
        )

    user = authenticate_user(email, password)

    if user is None:
        new_csrf_token = create_csrf_token()

        response = templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "csrf_token": new_csrf_token,
                "error": "Invalid email or password. Please try again.",
            },
            status_code=401,
        )

        set_csrf_cookie(response, new_csrf_token)

        return response

    # Create a new server-side session.
    session_token, expires_at = create_session(user["id"])

    response = RedirectResponse(
        url="/",
        status_code=303,
    )

    # Set the login cookie and rotate the CSRF token.
    set_session_cookie(response, session_token, expires_at)

    new_csrf_token = create_csrf_token()
    set_csrf_cookie(response, new_csrf_token)

    return response


# Display the Knowledge Assistant homepage.
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    user = get_current_user(request)

    # Require login before showing the Knowledge Assistant.
    if user is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    csrf_token = create_csrf_token()

    response = templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request,
            "user": user,
            "csrf_token": csrf_token,
        },
    )

    set_csrf_cookie(response, csrf_token)

    return response



# Receive a question and validate authentication and CSRF protection.
@app.post("/ask", response_class=HTMLResponse)
async def ask(
    request: Request,
    question: str = Form(...),
    csrf_token: str = Form(...),
):

    user = get_current_user(request)

    if user is None:
        return HTMLResponse(
            "Please log in before asking a question.",
            status_code=401,
        )

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

    if not validate_csrf_token(csrf_token, cookie_token):
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={
                "request": request,
                "message": "Your security token is invalid or expired.",
                "action": "Refresh the page and submit your question again.",
            },
            status_code=403,
        )

    # Reject questions that contain only spaces.
    if not question.strip():
        return templates.TemplateResponse(
            request=request,
            name="partials/error.html",
            context={
                "request": request,
                "message": "Your question is empty.",
                "action": "Enter a question before clicking Ask.",
            },
            status_code=422,
        )

    # Limit how frequently each client can search the policies.
    client_id = (
        request.client.host if request.client else "unknown"
    )
    check_rate_limit(client_id)

    # Search the policy documents for the user's question.
    matches = search_policies(question)

    # Prepare the answer and its source citation.
    if matches:
        answer = matches[0]["content"]

        sources = [
            {"source": matches[0]["source"]}
        ]
    else:
        answer = (
            "I couldn't find information about this question "
            "in the available policy documents. "
            "Try asking about leave, attendance, travel, "
            "or other company policies."
        )

        sources = []

    return templates.TemplateResponse(
        request=request,
        name="partials/answer.html",
        context={
            "request": request,
            "question": question,
            "answer": answer,
            "sources": sources,
        },
    )



# Log out and invalidate the server-side session.
@app.post("/logout")
async def logout(
    request: Request,
    csrf_token: str = Form(...),
):

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

    if not validate_csrf_token(csrf_token, cookie_token):
        return HTMLResponse(
            "Invalid or expired security token. Refresh the page.",
            status_code=403,
        )

    session_token = request.cookies.get(SESSION_COOKIE_NAME)

    if session_token:
        revoke_session(session_token)

    response = RedirectResponse(
        url="/login",
        status_code=303,
    )

    clear_session_cookie(response)
    clear_csrf_cookie(response)

    return response

# Allow access only to administrators.
@app.get("/admin")
async def admin_dashboard(request: Request):

    # Check whether the user is logged in.
    user = get_current_user(request)

    if user is None:
        return HTMLResponse(
            "Please log in first.",
            status_code=401,
        )

    # Check whether the logged-in user has the admin role.
    if not require_role(user, "admin"):
        return HTMLResponse(
            "Access denied. Administrator permission required.",
            status_code=403,
        )

    return HTMLResponse(
        "<h1>Admin Dashboard</h1>"
        "<p>Welcome, administrator.</p>"
    )

# Return a record only when the logged-in user owns it.
@app.get("/records/{record_id}")
async def read_record(record_id: int, request: Request):

    # Check whether the user is logged in.
    user = get_current_user(request)

    if user is None:
        return HTMLResponse(
            "Please log in first.",
            status_code=401,
        )

    # Retrieve the record only if the user owns it.
    record = get_owned_record(record_id, user)

    if record is None:
        return HTMLResponse(
            "Record not found.",
            status_code=404,
        )

    return {
        "id": record["id"],
        "title": record["title"],
        "content": record["content"],
    }

# Accept and safely store a text file uploaded by an authenticated user.
@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    csrf_token: str = Form(...),
):

    # Check whether the user is logged in.
    user = get_current_user(request)

    if user is None:
        return HTMLResponse(
            "Please log in before uploading a file.",
            status_code=401,
        )

    # Validate the CSRF token.
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)

    if not validate_csrf_token(csrf_token, cookie_token):
        return HTMLResponse(
            "Invalid or expired security token.",
            status_code=403,
        )

    # Check the file extension.
    if Path(file.filename or "").suffix.lower() != ".txt":
        return HTMLResponse(
            "Only .txt files are allowed.",
            status_code=400,
        )

    # Check the declared content type.
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return HTMLResponse(
            "Only plain text files are allowed.",
            status_code=400,
        )

    # Read the file in small chunks and enforce the size limit.
    content = bytearray()

    while True:
        chunk = await file.read(64 * 1024)

        if not chunk:
            break

        if len(content) + len(chunk) > MAX_UPLOAD_SIZE:
            await file.close()

            return HTMLResponse(
                "File is too large. Maximum size is 512 KB.",
                status_code=413,
            )

        content.extend(chunk)

    # Verify that the uploaded content is valid UTF-8 text.
    try:
        content.decode("utf-8")
    except UnicodeDecodeError:
        await file.close()

        return HTMLResponse(
            "Uploaded file must contain valid UTF-8 text.",
            status_code=400,
        )

    # Reject files containing null bytes.
    if b"\x00" in content:
        await file.close()

        return HTMLResponse(
            "Binary content is not allowed.",
            status_code=400,
        )

    # Generate a random server-side filename.
    stored_filename = f"{uuid.uuid4().hex}.txt"
    destination = UPLOAD_DIR / stored_filename

    # Save the uploaded content using the generated filename.
    destination.write_bytes(content)

    await file.close()

    return {
        "message": "File uploaded successfully.",
        "filename": stored_filename,
        "size": len(content),
    }
