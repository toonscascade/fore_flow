"""Authentication utilities: password hashing, validation, and session tokens.

Uses Argon2id (via argon2-cffi) for password hashing — the OWASP-recommended
algorithm for credential storage.
"""

import hashlib
import re
import secrets
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return _ph.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*, False otherwise."""
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# ---------------------------------------------------------------------------
# Password policy
# ---------------------------------------------------------------------------

def validate_password(password: str) -> list[str]:
    """Return a list of human-readable policy violations (empty = OK).

    Rules:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
    """
    errors: list[str] = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character")
    return errors


# ---------------------------------------------------------------------------
# Email helpers
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def valid_email(email: str) -> bool:
    """Quick RFC-ish email validation."""
    return bool(_EMAIL_RE.match(email))


def normalize_email(email: Optional[str]) -> Optional[str]:
    """Lower-case and strip whitespace from an email address."""
    if email is None:
        return None
    return email.strip().lower()


# ---------------------------------------------------------------------------
# Session tokens
# ---------------------------------------------------------------------------

def create_session_token() -> str:
    """Generate a cryptographically random session token (URL-safe, 64 chars)."""
    return secrets.token_urlsafe(48)


def token_digest(token: str) -> str:
    """SHA-256 digest of a raw session token for safe DB storage."""
    return hashlib.sha256(token.encode()).hexdigest()
