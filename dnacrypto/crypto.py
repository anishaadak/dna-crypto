import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


def make_key(password: str, salt: bytes) -> bytes:
    # turns a password into a 32-byte key (slow on purpose, so guessing is hard)
    kdf = Scrypt(salt=salt, length=32, n=2**15, r=8, p=1)
    return kdf.derive(password.encode())


def lock(message: str, password: str) -> bytes:
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = make_key(password, salt)
    locked = AESGCM(key).encrypt(nonce, message.encode(), None)
    return salt + nonce + locked      # keep all three together


def unlock(package: bytes, password: str) -> str:
    salt = package[:16]
    nonce = package[16:28]
    locked = package[28:]
    key = make_key(password, salt)
    return AESGCM(key).decrypt(nonce, locked, None).decode()