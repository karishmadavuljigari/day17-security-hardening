
from src.auth.audit import log_audit_event


# Define the roles supported by the application.
VALID_ROLES = {"employee", "admin"}


def has_role(user: dict, required_role: str) -> bool:
    """Check whether a user has the required role."""

    # Reject invalid roles.
    if required_role not in VALID_ROLES:
        return False

    # Check the user's assigned role.
    return user.get("role") == required_role


def require_role(user: dict, required_role: str) -> bool:
    """Check a role and record denied access."""

    if has_role(user, required_role):
        return True

    # Record the denied access attempt.
    log_audit_event(
        event_type="ACCESS_DENIED",
        user_id=user.get("id"),
        details={
            "required_role": required_role,
            "actual_role": user.get("role"),
        },
    )

    return False
