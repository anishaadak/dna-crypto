import pytest
from cryptography.exceptions import InvalidTag
from dnacrypto.encoding import bytes_to_dna, dna_to_bytes
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