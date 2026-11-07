from dnacrypto.encoding import bytes_to_dna_rot, explain_byte


def test_explain_all_values():
    for value in range(256):
        digits, steps = explain_byte(value, "A")
        assert len(digits) == 6
        assert all(d in (0, 1, 2) for d in digits)
        joined = "".join(step[2] for step in steps)
        assert joined == bytes_to_dna_rot(bytes([value]))


def test_explain_hello_world_carries_prev():
    data = b"hello world"
    expected = bytes_to_dna_rot(data)
    prev = "A"
    letters = []
    for byte in data:
        _, steps = explain_byte(byte, prev)
        for step in steps:
            prev = step[2]
        letters.extend(step[2] for step in steps)
    assert "".join(letters) == expected


def test_explain_invalid_value():
    try:
        explain_byte(256, "A")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for 256")


def test_explain_invalid_prev():
    try:
        explain_byte(5, "X")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for 'X'")
