import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from app.core.config import get_settings

password_hasher = PasswordHasher()
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, stored_password: str) -> tuple[bool, bool]:
    if not stored_password:
        return False, False
    if stored_password.startswith("$argon2"):
        try:
            valid = password_hasher.verify(stored_password, password)
            return valid, valid and password_hasher.check_needs_rehash(stored_password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False, False
    try:
        salt, expected = stored_password.split("$", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()
        return secrets.compare_digest(digest, expected), True
    except Exception:
        return False, False

def create_access_token(subject: str, role: str, institute_id: int | None, minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "institute_id": institute_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, get_settings().secret_key, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, get_settings().secret_key, algorithms=[ALGORITHM])
