import os

import pytest
from cryptography.exceptions import InvalidTag
from dnacrypto.encoding import (
    bytes_to_dna,
    bytes_to_dna_safe,
    dna_to_bytes,
    dna_to_bytes_safe,
    longest_run,
)
from dnacrypto.crypto import lock, unlock


def test_hi_encodes_correctly():
    assert bytes_to_dna(b"Hi") == "CAGACGGC"


def test_dna_round_trip():
    data = bytes(range(256))
    assert dna_to_bytes(bytes_to_dna(data)) == data


def test_lock_and_unlock():
    assert unlock(lock("hello", "pw"), "pw") == "hello"


def test_wrong_password_fails():
    with pytest.raises(InvalidTag):
        unlock(lock("hello", "pw"), "wrong")


def test_tampering_is_detected():
    package = bytearray(lock("hello", "pw"))
    package[-1] ^= 1                     # flip one bit
    with pytest.raises(InvalidTag):
        unlock(bytes(package), "pw")


def test_safe_round_trip_empty():
    assert dna_to_bytes_safe(bytes_to_dna_safe(b"")) == b""


def test_safe_round_trip_hi():
    assert dna_to_bytes_safe(bytes_to_dna_safe(b"Hi")) == b"Hi"


def test_safe_round_trip_zeros_50():
    assert dna_to_bytes_safe(bytes_to_dna_safe(b"\x00" * 50)) == b"\x00" * 50


def test_safe_round_trip_all_bytes():
    data = bytes(range(256))
    assert dna_to_bytes_safe(bytes_to_dna_safe(data)) == data


def test_safe_round_trip_random_lengths():
    for n in range(0, 41):
        data = os.urandom(n)
        assert dna_to_bytes_safe(bytes_to_dna_safe(data)) == data


def test_safe_longest_run_zeros_50_is_one():
    assert longest_run(bytes_to_dna_safe(b"\x00" * 50)) == 1


def test_original_longest_run_zeros_50_is_200():
    assert longest_run(bytes_to_dna(b"\x00" * 50)) == 200


def test_dna_to_bytes_safe_invalid_header_raises():
    with pytest.raises(ValueError):
        dna_to_bytes_safe("AAAA")