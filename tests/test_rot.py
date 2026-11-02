import os

import pytest

from dnacrypto.encoding import (
    bytes_to_dna_rot,
    dna_to_bytes_rot,
    longest_run,
)


def _replacement_letter(dna, i):
    forbidden = {dna[i]}
    if i > 0:
        forbidden.add(dna[i - 1])
    else:
        forbidden.add("A")
    if i < len(dna) - 1:
        forbidden.add(dna[i + 1])
    for c in "ACGT":
        if c not in forbidden:
            return c
    raise AssertionError("no replacement letter available")


def test_rot_round_trip_empty():
    assert dna_to_bytes_rot(bytes_to_dna_rot(b"")) == b""


def test_rot_round_trip_hi():
    assert dna_to_bytes_rot(bytes_to_dna_rot(b"Hi")) == b"Hi"


def test_rot_round_trip_all_bytes():
    data = bytes(range(256))
    assert dna_to_bytes_rot(bytes_to_dna_rot(data)) == data


def test_rot_round_trip_zeros_50():
    assert dna_to_bytes_rot(bytes_to_dna_rot(b"\x00" * 50)) == b"\x00" * 50


def test_rot_round_trip_random_lengths():
    for n in range(0, 41):
        data = os.urandom(n)
        assert dna_to_bytes_rot(bytes_to_dna_rot(data)) == data


def test_rot_length_is_six_times_data():
    for data in [b"", b"Hi", bytes(range(256)), b"\x00" * 50]:
        assert len(bytes_to_dna_rot(data)) == 6 * len(data)


def test_rot_longest_run_all_bytes_is_one():
    assert longest_run(bytes_to_dna_rot(bytes(range(256)))) == 1


def test_rot_longest_run_zeros_50_is_one():
    assert longest_run(bytes_to_dna_rot(b"\x00" * 50)) == 1


def test_rot_damage_stays_local():
    data = os.urandom(40)
    dna = bytes_to_dna_rot(data)
    for i in range(len(dna)):
        replacement = _replacement_letter(dna, i)
        copy = dna[:i] + replacement + dna[i + 1:]
        decoded = dna_to_bytes_rot(copy)
        diff_count = sum(1 for a, b in zip(decoded, data) if a != b)
        assert diff_count <= 2


def test_rot_invalid_length_raises():
    with pytest.raises(ValueError):
        dna_to_bytes_rot("ACG")


def test_rot_invalid_letter_raises():
    with pytest.raises(ValueError):
        dna_to_bytes_rot("ACGTAX")
