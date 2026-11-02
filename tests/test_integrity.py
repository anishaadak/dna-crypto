import pytest
from cryptography.exceptions import InvalidTag

from dnacrypto.ecc import add_parity, repair
from dnacrypto.encoding import bytes_to_dna_rot, dna_to_bytes_rot, longest_run
from dnacrypto.pipeline import (
    check_dna,
    decrypt_from_dna,
    damage_letter,
    encrypt_to_dna,
    repair_dna,
    seal,
    unseal,
)

PASSWORD = "pw"
MESSAGE = "hello"
DNA = encrypt_to_dna(MESSAGE, PASSWORD)


def test_round_trip():
    assert decrypt_from_dna(DNA, "pw") == "hello"


def test_longest_run_is_one():
    assert longest_run(DNA) == 1


def test_check_intact():
    assert check_dna(DNA, "pw")[0] == "intact"


def test_check_no_password():
    assert check_dna(DNA)[0] == "no_damage_found"


def test_check_wrong_password():
    assert check_dna(DNA, "wrong")[0] == "wrong_password_or_tampered"


def test_one_wrong_letter():
    damaged = damage_letter(DNA, 100)
    assert check_dna(damaged)[0] == "repairable"
    assert decrypt_from_dna(damaged, "pw") == "hello"
    repaired_dna, positions = repair_dna(damaged)
    assert repaired_dna == DNA
    assert len(positions) in (1, 2)


def test_three_wrong_letters():
    damaged = damage_letter(DNA, 40)
    damaged = damage_letter(damaged, 200)
    damaged = damage_letter(damaged, 360)
    assert decrypt_from_dna(damaged, "pw") == "hello"


def test_heavy_damage():
    damaged = DNA
    for i in (10, 30, 50, 70, 90, 110, 130, 150, 170, 190, 210, 230):
        damaged = damage_letter(damaged, i)
    assert check_dna(damaged)[0] in ("too_damaged", "changed")
    with pytest.raises((ValueError, InvalidTag)):
        decrypt_from_dna(damaged, "pw")


def test_truncated_invalid():
    assert check_dna(DNA[:-3])[0] == "invalid_dna"


def test_bad_letter_invalid():
    tampered = DNA[:50] + "X" + DNA[50:]
    assert check_dna(tampered)[0] == "invalid_dna"


def test_smart_tampering():
    data = dna_to_bytes_rot(DNA)
    message, _ = repair(data)
    body = bytearray(unseal(message))
    body[20] ^= 1
    dna2 = bytes_to_dna_rot(add_parity(seal(bytes(body))))
    assert check_dna(dna2, "pw")[0] == "wrong_password_or_tampered"
    assert check_dna(dna2)[0] == "no_damage_found"
    # without the password, an attacker who recomputes the checksum and the repair data is not detected
