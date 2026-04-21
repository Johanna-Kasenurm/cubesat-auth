import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

password_hasher = PasswordHasher()

# Hash a plaintext password with Argon2
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

# Verify a plaintext password against a stored password hash
def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except VerifyMismatchError:
        return False

# Generate a secure random session token
def generate_token() -> str:
    return secrets.token_urlsafe(32)

# Hash a session token for storage
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()