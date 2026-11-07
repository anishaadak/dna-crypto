from dnacrypto.pipeline import decrypt_from_dna, encrypt_steps


def test_steps_decrypt_round_trip():
    steps = encrypt_steps("hello", "pw")
    assert decrypt_from_dna(steps["dna"], "pw") == "hello"


def test_steps_lengths():
    steps = encrypt_steps("hello", "pw")
    assert len(steps["salt"]) == 16
    assert len(steps["nonce"]) == 12
    assert len(steps["tag"]) == 16
    assert len(steps["ciphertext"]) == 5
    assert len(steps["checksum"]) == 4
    assert steps["parity_len"] == 16
    assert len(steps["coded"]) == 69
    assert len(steps["dna"]) == 414


def test_steps_no_password_or_key():
    steps = encrypt_steps("hello", "pw")
    for key in steps:
        assert "password" not in key
        assert "key" not in key


def test_steps_namaste():
    steps = encrypt_steps("नमस्ते", "pw")
    assert decrypt_from_dna(steps["dna"], "pw") == "नमस्ते"
