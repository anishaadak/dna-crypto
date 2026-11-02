import os
import random

import pytest

from dnacrypto.ecc import add_parity, repair, PARITY


def test_add_parity_length():
    assert len(add_parity(b"hello")) == 21


def test_repair_no_damage():
    data = os.urandom(100)
    assert repair(add_parity(data)) == (data, [])


def test_repair_eight_damaged_positions():
    data = os.urandom(100)
    encoded = bytearray(add_parity(data))
    positions = random.sample(range(len(encoded)), 8)
    for i in positions:
        encoded[i] ^= random.randint(1, 255)
    message, fixed_positions = repair(bytes(encoded))
    assert message == data
    assert sorted(fixed_positions) == sorted(positions)


def test_repair_six_hundred_bytes_three_damaged():
    data = os.urandom(600)
    encoded = bytearray(add_parity(data))
    positions = random.sample(range(len(encoded)), 3)
    for i in positions:
        encoded[i] ^= random.randint(1, 255)
    message, fixed_positions = repair(bytes(encoded))
    assert message == data
    assert sorted(fixed_positions) == sorted(positions)


def test_repair_twelve_damaged_positions():
    data = os.urandom(100)
    encoded = bytearray(add_parity(data))
    positions = random.sample(range(len(encoded)), 12)
    for i in positions:
        encoded[i] ^= random.randint(1, 255)
    try:
        message, fixed_positions = repair(bytes(encoded))
    except ValueError:
        return
    assert message != data


def test_repair_too_short():
    with pytest.raises(ValueError):
        repair(b"abc")
