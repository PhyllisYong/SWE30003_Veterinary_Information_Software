import os
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional
import bcrypt as _bcrypt
from jose import JWTError, jwt

# ── Configuration ──────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-use-a-long-random-string")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ── Password hashing ───────────────────────────────────────────────────────────
# passlib 1.7.4 is incompatible with bcrypt 4.x / 5.x, so we call bcrypt directly.


def _prehash(password: str) -> bytes:
    """
    SHA-256 pre-hash before bcrypt.

    bcrypt hard-limits input to 72 bytes. Pre-hashing with SHA-256 produces a
    fixed 32-byte digest (44 chars as base64), always well under that limit,
    while preserving full entropy for passwords of any length.
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)          # bytes, not str — bcrypt wants bytes


def hashPassword(password: str) -> str:
    """Hash a plain-text password using SHA-256 + bcrypt."""
    return _bcrypt.hashpw(_prehash(password), _bcrypt.gensalt()).decode("utf-8")


def verifyPassword(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its SHA-256 + bcrypt hash."""
    return _bcrypt.checkpw(_prehash(plain_password), hashed_password.encode("utf-8"))


# ── JWT tokens ─────────────────────────────────────────────────────────────────
def generateToken(userID: str, role: str) -> str:
    """Generate a JWT access token for the given userID and role."""
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": userID,
        "role": role,
        "exp": expires,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def validateToken(token: str) -> Optional[dict]:
    """
    Validate a JWT token and return the payload dict, or None if invalid.
    Payload contains: { "sub": userID, "role": role }
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None