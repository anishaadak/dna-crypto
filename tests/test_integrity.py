from dnacrypto.encoding import bytes_to_dna_safe, dna_to_bytes_safe
from dnacrypto.pipeline import (
    check_dna,
    decrypt_from_dna,
    encrypt_to_dna,
    seal,
)


def change_letter(dna, i):
    forbidden = {dna[i]}
    if i > 0:
        forbidden.add(dna[i - 1])
    if i < len(dna) - 1:
        forbidden.add(dna[i + 1])
    for c in "ACGT":
        if c not in forbidden:
            return dna[:i] + c + dna[i + 1:]
    raise AssertionError("no replacement letter available")


PASSWORD = "pw"
MESSAGE = "hello"
DNA = encrypt_to_dna(MESSAGE, PASSWORD)


def test_round_trip():
    assert decrypt_from_dna(encrypt_to_dna("hello", "pw"), "pw") == "hello"


def test_check_intact():
    assert check_dna(DNA, "pw")[0] == "intact"


def test_check_no_password():
    assert check_dna(DNA)[0] == "no_damage_found"


def test_check_wrong_password():
    assert check_dna(DNA, "wrong")[0] == "wrong_password_or_tampered"


def test_check_changed_letter():
    assert check_dna(change_letter(DNA, 100))[0] == "changed"


def test_check_repeated_letter():
    tampered = DNA[:100] + DNA[99] + DNA[101:]
    assert check_dna(tampered)[0] == "invalid_dna"


def test_check_truncated():
    assert check_dna(DNA[:-3])[0] == "invalid_dna"


def test_check_bad_letter():
    tampered = DNA[:50] + "X" + DNA[50:]
    assert check_dna(tampered)[0] == "invalid_dna"


def test_smart_tampering():
    data = dna_to_bytes_safe(DNA)
    body = bytearray(data[:-4])
    body[20] ^= 1  # flip one bit in the sealed body
    dna2 = bytes_to_dna_safe(seal(bytes(body)))
    assert check_dna(dna2, "pw")[0] == "wrong_password_or_tampered"
    assert check_dna(dna2)[0] == "no_damage_found"
    # without the password, an attacker who fixes the checksum is not detected
