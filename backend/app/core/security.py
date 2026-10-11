
import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from pwdlib import PasswordHash

load_dotenv()

# JWT configuration
SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Convert plain password into a secure hash."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify entered password against stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(user_id: int) -> str:
    """Generate a JWT token valid for 60 minutes."""

    expire = datetime.now(timezone.utc) + timedelta(minutes=60)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
