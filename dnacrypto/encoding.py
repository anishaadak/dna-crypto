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


def _digits_needed(n_bytes: int) -> int:
    if n_bytes == 0:
        return 0
    limit = 256 ** n_bytes
    k = 0
    power = 1
    while power < limit:
        k += 1
        power *= 3
    return k


def _encode_segment(data: bytes, prev: str) -> str:
    k = _digits_needed(len(data))
    number = int.from_bytes(data, "big")
    digits = []
    for _ in range(k):
        digits.append(number % 3)
        number //= 3
    digits.reverse()
    output = []
    for d in digits:
        allowed = [x for x in "ACGT" if x != prev]
        letter = allowed[d]
        output.append(letter)
        prev = letter
    return "".join(output)


def _decode_segment(dna: str, n_bytes: int, prev: str) -> bytes:
    number = 0
    for letter in dna:
        allowed = [x for x in "ACGT" if x != prev]
        if letter not in allowed:
            raise ValueError
        d = allowed.index(letter)
        number = number * 3 + d
        prev = letter
    if number >= 256 ** n_bytes:
        raise ValueError
    return number.to_bytes(n_bytes, "big")


def bytes_to_dna_safe(data: bytes) -> str:
    length_dna = _encode_segment(len(data).to_bytes(4, "big"), "A")
    data_dna = _encode_segment(data, length_dna[-1])
    return length_dna + data_dna


def dna_to_bytes_safe(dna: str) -> bytes:
    header_len = _digits_needed(4)
    if len(dna) < header_len:
        raise ValueError
    n_bytes = _decode_segment(dna[:header_len], 4, "A")
    n = int.from_bytes(n_bytes, "big")
    rest = dna[header_len:]
    if len(rest) != _digits_needed(n):
        raise ValueError
    return _decode_segment(rest, n, dna[header_len - 1])


def gc_content(dna: str) -> float:
    if not dna:
        return 0.0
    return sum(1 for letter in dna if letter in "GC") / len(dna)


def longest_run(dna: str) -> int:
    if not dna:
        return 0
    best = 1
    current = 1
    for i in range(1, len(dna)):
        if dna[i] == dna[i - 1]:
            current += 1
            if current > best:
                best = current
        else:
            current = 1
    return best


def bytes_to_dna_rot(data: bytes) -> str:
    prev = "A"
    output = []
    for byte in data:
        digits = []
        n = byte
        for _ in range(6):
            digits.append(n % 3)
            n //= 3
        digits.reverse()
        for d in digits:
            allowed = [x for x in "ACGT" if x != prev]
            letter = allowed[d]
            output.append(letter)
            prev = letter
    return "".join(output)


def dna_to_bytes_rot(dna: str) -> bytes:
    if len(dna) % 6 != 0:
        raise ValueError
    for c in dna:
        if c not in "ACGT":
            raise ValueError
    prev = "A"
    result = bytearray()
    for i in range(0, len(dna), 6):
        group = dna[i:i + 6]
        value = 0
        for letter in group:
            allowed = [x for x in "ACGT" if x != prev]
            if letter in allowed:
                d = allowed.index(letter)
            else:
                d = 0
            value = value * 3 + d
            prev = letter
        if value > 255:
            value = 0
        result.append(value)
    return bytes(result)


def explain_byte(value: int, prev: str) -> tuple[list[int], list[tuple[str, list[str], str]]]:
    if not 0 <= value <= 255:
        raise ValueError
    if prev not in "ACGT":
        raise ValueError
    digits = []
    n = value
    for _ in range(6):
        digits.append(n % 3)
        n //= 3
    digits.reverse()
    steps = []
    current = prev
    for d in digits:
        allowed = [x for x in "ACGT" if x != current]
        letter = allowed[d]
        steps.append((current, allowed, letter))
        current = letter
    return digits, steps