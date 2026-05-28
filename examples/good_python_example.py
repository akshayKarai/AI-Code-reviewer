"""
Example: Well-written Python code with proper patterns.
Use this to see how the AI Code Reviewer scores clean code.
"""

import sqlite3
import hashlib
import secrets
import logging
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection(db_path: str):
    """Context manager for safe database connections."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_user(username: str) -> Optional[tuple]:
    """Fetch user by username using parameterised query (safe from SQL injection)."""
    with get_db_connection("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password with a salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return hashed, salt


def login(username: str, password: str) -> bool:
    """Authenticate a user with hashed password comparison."""
    user = get_user(username)
    if not user:
        logger.warning("Login attempt for unknown user: %s", username)
        return False
    stored_hash, salt = user[2], user[3]
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, stored_hash)


def calculate_average(numbers: list[float]) -> float:
    """Calculate average with input validation."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list.")
    return sum(numbers) / len(numbers)


def create_session(user_id: str) -> str:
    """Create a cryptographically secure session token."""
    return secrets.token_urlsafe(32)
