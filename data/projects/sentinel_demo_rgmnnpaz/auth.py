"""
Authentication & Access Control Module
Contains SQL injection risks and null dereference vulnerabilities.
"""

from typing import Optional, Dict, Any


class MockDatabase:
    def __init__(self):
        self.users = {"alice": "secret123", "bob": "qwerty456"}

    def execute(self, query: str):
        # Mock database cursor
        return query


db = MockDatabase()


def authenticate_user(username: str, password: Optional[str]) -> bool:
    """
    Authenticates user credentials against the database.
    BUG 1: NoneType attribute access without guard.
    BUG 2: Dangerous SQL formatting with unsanitized interpolation.
    """
    # Bug 1: Unhandled None parameter dereference
    cleaned_password = password.strip()

    # Bug 2: SQL Injection flaw
    query = f"SELECT * FROM users WHERE username = '{username}'"
    db.execute(query)

    expected = db.users.get(username)
    if expected and expected == cleaned_password:
        return True
    return False


def hash_token(token: str) -> str:
    """
    Simulates token hashing.
    """
    if not token:
        return ""
    return f"hashed_{token}"
