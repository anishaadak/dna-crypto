import zlib

from cryptography.exceptions import InvalidTag

from dnacrypto.crypto import lock, unlock
from dnacrypto.encoding import bytes_to_dna_safe, dna_to_bytes_safe


def seal(package: bytes) -> bytes:
    return package + zlib.crc32(package).to_bytes(4, "big")


def unseal(data: bytes) -> bytes:
    if len(data) < 4:
        raise ValueError
    body = data[:-4]
    if zlib.crc32(body).to_bytes(4, "big") != data[-4:]:
        raise ValueError("checksum mismatch")
    return body


def encrypt_to_dna(message: str, password: str) -> str:
    return bytes_to_dna_safe(seal(lock(message, password)))


def decrypt_from_dna(dna: str, password: str) -> str:
    return unlock(unseal(dna_to_bytes_safe(dna)), password)


def check_dna(dna: str, password=None) -> tuple[str, str]:
    dna = "".join(dna.split()).upper()

    # a. any letter not in ACGT
    for i, c in enumerate(dna, start=1):
        if c not in "ACGT":
            return (
                "invalid_dna",
                f"Letter {i} is '{c}', which is not A, C, G or T.",
            )

    # b. two neighbouring letters are the same
    for i in range(len(dna) - 1):
        if dna[i] == dna[i + 1]:
            c = dna[i]
            return (
                "invalid_dna",
                f"Letters {i + 1} and {i + 2} are both '{c}'. "
                "The safe encoding never repeats a letter, so something was changed near here.",
            )

    # c. structure is wrong
    try:
        decoded = dna_to_bytes_safe(dna)
    except ValueError:
        return (
            "invalid_dna",
            "The length or structure is wrong. Letters were probably added, lost or changed.",
        )

    # d. decoded bytes are too short
    if len(decoded) < 48:
        return ("invalid_dna", "The DNA is too short to be valid.")

    # e. checksum mismatch
    try:
        body = unseal(decoded)
    except ValueError:
        return (
            "changed",
            "The checksum does not match. The DNA was changed after it was written. "
            "This is most likely accidental damage, but it could also be an edit.",
        )

    # f. no password to confirm with
    if password is None:
        return (
            "no_damage_found",
            "No damage found. Without the password I cannot fully confirm it is intact.",
        )

    # g. wrong password or deliberate tampering
    try:
        unlock(body, password)
    except InvalidTag:
        return (
            "wrong_password_or_tampered",
            "The data matches its checksum but will not decrypt. Most likely the password is wrong. "
            "Deliberate tampering that also fixed the checksum would look the same.",
        )

    # h. everything checks out
    return ("intact", "Decrypts correctly. Nothing was changed.")
