
import re
import requests

# Create a browser-like session.
session = requests.Session()

# Open the homepage and retrieve the CSRF token.
page = session.get("http://127.0.0.1:8000/")

token_match = re.search(
    r'name="csrf_token"\s+value="([^"]+)"',
    page.text,
)

if not token_match:
    raise RuntimeError("CSRF token not found on homepage")

csrf_token = token_match.group(1)

# Submit a question containing a script tag.
payload = '<script>alert("XSS")</script>'

response = session.post(
    "http://127.0.0.1:8000/ask",
    data={
        "question": payload,
        "csrf_token": csrf_token,
    },
)

# Check the response.
print("Status:", response.status_code)
print("Response:", response.text)
print("Script escaped:", "&lt;script&gt;" in response.text)
print("Executable script tag present:", "<script>" in response.text)
