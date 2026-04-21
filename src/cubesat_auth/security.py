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

