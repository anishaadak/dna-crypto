from reedsolo import RSCodec, ReedSolomonError

PARITY = 16


def add_parity(data: bytes) -> bytes:
    return bytes(RSCodec(PARITY).encode(data))


def repair(data: bytes) -> tuple[bytes, list[int]]:
    if len(data) <= PARITY:
        raise ValueError("too short")
    rsc = RSCodec(PARITY)
    try:
        result = rsc.decode(data)
    except ReedSolomonError:
        raise ValueError("too damaged to repair")
    message = result[0] if isinstance(result, tuple) else result
    message = bytes(message)
    fixed = bytes(rsc.encode(message))
    positions = [i for i, (a, b) in enumerate(zip(data, fixed)) if a != b]
    return (message, positions)
