
import time
from collections import defaultdict, deque
from fastapi import HTTPException


# Store request timestamps separately for each client.
request_history = defaultdict(deque)


# Check whether a client has exceeded the request limit.
def check_rate_limit(
    client_id: str,
    max_requests: int = 5,
    window_seconds: int = 60,
):
    # Get the current time.
    current_time = time.time()

    # Get this client's request history.
    timestamps = request_history[client_id]

    # Remove requests that are outside the time window.
    while timestamps and timestamps[0] <= current_time - window_seconds:
        timestamps.popleft()

    # Check whether the client has reached the request limit.
    if len(timestamps) >= max_requests:
        # Calculate how long the client must wait.
        retry_after = int(
            timestamps[0] + window_seconds - current_time
        ) + 1

        # Reject the request with HTTP 429.
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # Record the current request because it is allowed.
    timestamps.append(current_time)
