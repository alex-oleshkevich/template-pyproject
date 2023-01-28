import passlib.context
from passlib.handlers.pbkdf2 import pbkdf2_sha256

password_hasher = passlib.context.CryptContext(default=pbkdf2_sha256, schemes=[pbkdf2_sha256])


def generate_password_hash(password: str) -> str:
    """Hash given password using selected hashing method."""
    return password_hasher.hash(password)


def check_password_hash(plain_password: str, hashed_password: str) -> bool:
    """Verify given password hash using selected hashing method."""
    return password_hasher.verify(plain_password, hashed_password)
