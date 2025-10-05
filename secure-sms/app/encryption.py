"""Encryption utilities for storing sensitive data.

This module wraps ``cryptography.fernet.Fernet`` to encrypt and decrypt
strings.  The encryption key is loaded from the ``ENCRYPTION_KEY``
environment variable.  Functions return sensible fallbacks when a
fernet instance is not configured or when decryption fails.
"""

from cryptography.fernet import Fernet, InvalidToken
import os


# Internal module‑level variables to cache the key and Fernet instance
_key: bytes | None = os.getenv("ENCRYPTION_KEY", "").encode()
_fernet: Fernet | None = None
if _key:
    try:
        _fernet = Fernet(_key)
    except Exception:
        _fernet = None


def get_fernet() -> Fernet | None:
    """Return a cached or freshly loaded Fernet instance, if possible."""
    global _fernet
    if _fernet is None:
        # Try to load again (in case env was set later)
        key = os.getenv("ENCRYPTION_KEY", "").encode()
        if key:
            _fernet = Fernet(key)
    return _fernet


def encrypt_text(text: str | None) -> bytes | None:
    """Encrypt a plaintext string and return the ciphertext.

    Args:
        text: Plaintext string to encrypt.

    Returns:
        The encrypted bytes, or ``None`` if encryption cannot be performed
        (e.g. missing key or ``text`` is ``None``).
    """
    f = get_fernet()
    if not f or text is None:
        return None
    return f.encrypt(text.encode("utf-8"))


def decrypt_text(token: bytes | None) -> str:
    """Decrypt an encrypted token back to a plaintext string.

    Args:
        token: Encrypted bytes to decrypt.

    Returns:
        The decrypted plaintext string, or an empty string on failure.
    """
    f = get_fernet()
    if not f or not token:
        return ""
    try:
        return f.decrypt(token).decode("utf-8")
    except InvalidToken:
        # return placeholder to avoid crashes
        return "[decryption failed]"