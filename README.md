# DNA Crypto

Encrypts a message with a password and writes the result as a string of DNA letters (A, C, G, T). It can also turn the DNA back into the original message using the same password.

## How it works

message -> encrypt with AES-256-GCM (key from password using scrypt) -> bytes -> DNA letters -> bytes -> decrypt -> message

Each byte becomes 8 bits, and every pair of bits maps to one DNA letter:

| Bits | Letter |
|------|--------|
| 00   | A      |
| 01   | C      |
| 10   | G      |
| 11   | T      |

So 1 byte becomes exactly 4 DNA letters. For example, encoding the raw text "Hi" with only the DNA step gives:

`CAGACGGC`

The real program encodes the *encrypted* bytes, so its output looks random. The encrypted data also carries a 16-byte salt, a 12-byte nonce and a 16-byte authentication tag. The DNA length is therefore 4 × (message bytes + 44) letters. For example, "hello" gives 196 letters.

Decoding works the other way: letters turn back into bits, bits turn back into bytes, and the password unlocks the original message.

Decoding works the other way: letters turn back into bits, bits turn back into bytes, and the password unlocks the original message.

## Security note

The security comes from AES-256-GCM and scrypt, which are standard, well-tested algorithms from the cryptography library. The DNA letters are only a different way of writing the encrypted bytes.

This project is not a new cipher, and the DNA step does not make it stronger.

## Setup

```bash
python -m venv .venv
```

Activate it:

- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

Then install:

```bash
pip install cryptography pytest
```

## Usage

Run the demo:

```bash
python main.py
```

Or use the command line:

```bash
python -m dnacrypto.cli encrypt --text "hello"
python -m dnacrypto.cli decrypt --dna "PASTE_DNA_HERE"
```

The password is asked for interactively and is not shown while you type it.

## Tests

```bash
python -m pytest
```

## Project structure

```
dnacrypto/
  encoding.py   # bytes <-> DNA letters
  crypto.py     # lock/unlock with AES-GCM
  cli.py        # encrypt and decrypt commands
tests/
  test_basic.py # tests
main.py         # demo
```
## Limitations

- The DNA step is only an encoding. It is not a security feature, and the project is not a new cipher.
- A weak password is still weak. The strength of the encryption depends on the password.
- There is no error correction, so one wrong letter makes decryption fail.
- The DNA output is not designed for real DNA synthesis. It can contain long runs of the same letter, which real labs avoid.
- This is a learning project and has not been security-audited. Do not use it to protect sensitive data.