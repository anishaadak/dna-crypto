import zlib

from cryptography.exceptions import InvalidTag

from dnacrypto.crypto import lock, unlock
from dnacrypto.ecc import add_parity, repair
from dnacrypto.encoding import bytes_to_dna_rot, dna_to_bytes_rot


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
    return bytes_to_dna_rot(add_parity(seal(lock(message, password))))


def decrypt_from_dna(dna: str, password: str) -> str:
    dna = "".join(dna.split()).upper()
    data = dna_to_bytes_rot(dna)
    message, _ = repair(data)
    return unlock(unseal(message), password)


def damage_letter(dna, i) -> str:
    dna = "".join(dna.split()).upper()
    forbidden = {dna[i]}
    if i > 0:
        forbidden.add(dna[i - 1])
    else:
        forbidden.add("A")
    if i < len(dna) - 1:
        forbidden.add(dna[i + 1])
    for c in "ACGT":
        if c not in forbidden:
            return dna[:i] + c + dna[i + 1:]
    raise AssertionError("no replacement letter available")


def repair_dna(dna) -> tuple[str, list[int]]:
    dna = "".join(dna.split()).upper()
    data = dna_to_bytes_rot(dna)
    message, positions = repair(data)
    return bytes_to_dna_rot(add_parity(message)), positions


def check_dna(dna: str, password=None) -> tuple[str, str]:
    dna = "".join(dna.split()).upper()

    # a. any letter not in ACGT
    for i, c in enumerate(dna, start=1):
        if c not in "ACGT":
            return (
                "invalid_dna",
                f"Letter {i} is '{c}', which is not A, C, G or T.",
            )

    # b. length not a multiple of 6
    if len(dna) % 6 != 0:
        return (
            "invalid_dna",
            "The length is not a multiple of 6, so letters were added or lost. "
            "This tool can fix changed letters, but not added or lost ones.",
        )

    # c. decode rot and check length
    data = dna_to_bytes_rot(dna)
    if len(data) < 64:
        return ("invalid_dna", "The DNA is too short to be valid.")

    # d. repair
    try:
        message, positions = repair(data)
    except ValueError:
        return (
            "too_damaged",
            "There is more damage than the repair code can fix (about 8 damaged bytes per 255-byte block).",
        )

    # e. positions not empty
    if positions:
        ranges = []
        for p in positions[:5]:
            ranges.append(f"{6 * p + 1}-{6 * p + 6}")
        text = ", ".join(ranges)
        return (
            "repairable",
            f"Damage found in {len(positions)} byte(s), at letters {text}. "
            "Run the repair command to fix it.",
        )

    # f. unseal mismatch
    try:
        unsealed = unseal(message)
    except ValueError:
        return (
            "changed",
            "The repair code is satisfied but the checksum does not match. "
            "The data was probably edited on purpose.",
        )

    # g. no password
    if password is None:
        return (
            "no_damage_found",
            "No damage found. Without the password I cannot fully confirm it is intact.",
        )

    # h. wrong password or deliberate tampering
    try:
        unlock(unsealed, password)
    except InvalidTag:
        return (
            "wrong_password_or_tampered",
            "The data matches its checksum but will not decrypt. Most likely the password is wrong. "
            "Deliberate tampering that also fixed the checksum would look the same.",
        )

    # i. intact
    return ("intact", "Decrypts correctly. Nothing was changed.")
