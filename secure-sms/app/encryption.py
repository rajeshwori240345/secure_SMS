import os
from cryptography.fernet import Fernet, InvalidToken

_key = os.getenv("ENCRYPTION_KEY", "").encode()
_fernet = None
if _key:
    try:
        _fernet = Fernet(_key)
    except Exception:
        _fernet = None

def get_fernet():
    global _fernet
    if _fernet is None:
        # Try to load again (in case env was set later)
        key = os.getenv("ENCRYPTION_KEY", "").encode()
        if key:
            _fernet = Fernet(key)
    return _fernet

def encrypt_text(text: str) -> bytes:
    f = get_fernet()
    if not f or text is None:
        return None
    return f.encrypt(text.encode("utf-8"))

def decrypt_text(token: bytes) -> str:
    f = get_fernet()
    if not f or not token:
        return ""
    try:
        return f.decrypt(token).decode("utf-8")
    except InvalidToken:
        # return placeholder to avoid crashes
        return "[decryption failed]"
