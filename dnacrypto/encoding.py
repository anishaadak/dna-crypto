MAP = {"00": "A", "01": "C", "10": "G", "11": "T"}
REVERSE = {letter: bits for bits, letter in MAP.items()}


def bytes_to_dna(data: bytes) -> str:
    # 1. turn every byte into 8 bits, e.g. 72 -> "01001000"
    bits = "".join(format(byte, "08b") for byte in data)
    # 2. take the bits two at a time and swap each pair for a letter
    return "".join(MAP[bits[i:i + 2]] for i in range(0, len(bits), 2))


def dna_to_bytes(dna: str) -> bytes:
    # reverse: letters -> bits -> bytes
    bits = "".join(REVERSE[letter] for letter in dna)
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))