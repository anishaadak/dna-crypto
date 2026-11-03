# DNA Crypto

LIVE DEMO APP: https://dna-crypto-sw3pbuplvpvfbamcbrscop.streamlit.app/

Encrypts a message with a password and writes the result as a string of DNA letters (A, C, G, T). It can turn the DNA back into the original message, check whether DNA has been damaged, and repair changed letters.

## How it works

```
message -> encrypt with AES-256-GCM (key from password using scrypt) -> add checksum -> add repair data -> DNA letters
DNA letters -> repair damaged bytes -> check checksum -> decrypt -> message
 ```

Each byte becomes 8 bits, and every pair of bits maps to one DNA letter:

| Bits | Letter |
|------|--------|
| 00   | A      |
| 01   | C      |
| 10   | G      |
| 11   | T      |

So 1 byte becomes exactly 4 DNA letters. For example, the text "Hi" becomes `CAGACGGC` with this mapping. This is the simple version of the idea. The program itself uses the safer encoding described in the next section.

The real program encodes the encrypted bytes, plus a checksum and repair data, so its output looks random. For short messages (up to about 190 bytes) its DNA has 6 x (message bytes + 64) letters. For example, the message hello gives 414 letters.

## DNA encoding and error correction

Real DNA labs have trouble with long runs of the same letter, and real DNA gets damaged. So before writing the DNA, the program adds repair data and writes each byte in a way that never repeats a letter.

### The journey of a message

```
message
  |  encrypt with AES-256-GCM (key from password, using scrypt)
  v
salt + nonce + encrypted message + tag
  |  add a 4-byte checksum (CRC32)
  |  add 16 bytes of Reed-Solomon repair data
  v
bytes
  |  write each byte as 6 DNA letters (a letter never repeats)
  v
DNA
```

Reading the DNA back runs the same steps in reverse: DNA to bytes, repair damaged bytes, check the checksum, decrypt.

### What the bytes contain

| Part | Size | Purpose |
|---|---|---|
| Salt | 16 bytes | Turns the password into a key |
| Nonce | 12 bytes | Makes every encryption unique |
| Encrypted message and tag | message length + 16 bytes | The locked message, and the seal that detects changes |
| Checksum | 4 bytes | Detects accidental damage without the password |
| Repair data | 16 bytes per block | Fixes damaged bytes |

The message hello (5 bytes) becomes 5 + 16 + 12 + 16 + 4 + 16 = 69 bytes, which is 69 x 6 = 414 letters.

### One byte becomes 6 letters

A byte is a number from 0 to 255. Written with the digits 0, 1 and 2 (base 3) it needs 6 digits, because 3^6 = 729 is enough to cover all 256 values. Each digit picks one of the three letters that are different from the previous letter:

| Previous letter | Digit 0 | Digit 1 | Digit 2 |
|---|---|---|---|
| A | C | G | T |
| C | A | G | T |
| G | A | C | T |
| T | A | C | G |

Example: the byte value 5 is written as the digits 0, 0, 0, 0, 1, 2. Starting after the letter A, these digits pick C, A, C, A, G, T. So 5 becomes CACAGT, and no letter repeats.

Each byte is encoded on its own, so one wrong letter damages only one or two bytes. If the whole message were encoded as one big number, one wrong letter would change almost everything and nothing could be repaired.

### How repair works

Reed-Solomon adds repair data. It is the same family of codes used in QR codes and CDs. When the DNA is read back, the repair data lets the program find which bytes are wrong and work out what they should be.

| What | Value |
|---|---|
| Repair data | 16 bytes added to every block of up to 239 data bytes (255 bytes in total) |
| Can fix | Up to 8 damaged bytes per block |
| One wrong letter damages | 1 byte, sometimes 2 |
| So roughly | 4 to 8 wrong letters per block |
| Cannot fix | Letters that were added or lost, or damage beyond the limit |

| Damage | What the program does |
|---|---|
| A few letters changed | check says REPAIRABLE, repair fixes it, and decrypt repairs it automatically |
| Too many letters changed | check says TOO_DAMAGED, and repair and decrypt refuse |
| Letters added or lost | check says INVALID_DNA, and it cannot be repaired |

### The cost

The DNA is about twice as long as the plain 2-bits-per-letter mapping. The message hello becomes 414 letters instead of about 200. That is the price of never repeating a letter and being able to repair damage.

## Checking DNA for damage

```bash
python -m dnacrypto.cli check --dna "PASTE_DNA_HERE"
```

The check reports one of these results:

| Result | Meaning |
|---|---|
| INVALID_DNA | Wrong letters, or the length is not a multiple of 6 (letters were added or lost) |
| REPAIRABLE | Some letters were changed, and the repair code can fix them |
| TOO_DAMAGED | More letters were changed than the repair code can fix |
| CHANGED | The repair code is satisfied but the checksum does not match, so the data was probably edited on purpose |
| WRONG_PASSWORD_OR_TAMPERED | The checksum matches but decryption fails. Most likely the password is wrong |
| INTACT | Decrypts correctly (needs the password) |
| NO_DAMAGE_FOUND | Nothing looks wrong, but this cannot be confirmed without the password |

The check only reports. To fix damaged letters, use the repair command.

The check cannot tell accidental damage from a deliberate edit. The checksum and repair data catch accidents without the password, but anyone can recompute them. Real tamper protection comes from the AES-GCM tag, which needs the password.

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
pip install cryptography reedsolo pytest
```

## Usage

Run the demo (it also damages one letter on purpose and repairs it):

```bash
python main.py
```

Or use the command line:

```bash
python -m dnacrypto.cli encrypt --text "hello"
python -m dnacrypto.cli decrypt --dna "PASTE_DNA_HERE"
python -m dnacrypto.cli check --dna "PASTE_DNA_HERE"
python -m dnacrypto.cli repair --dna "PASTE_DNA_HERE"
```

The password is asked for interactively and is not shown while you type it. Repair does not need the password, and it prints the fixed DNA. The decrypt command also repairs small damage automatically.

## Tests

```bash
python -m pytest
```

## Project structure

```
dnacrypto/
  encoding.py   # bytes <-> DNA letters
  crypto.py     # lock/unlock with AES-GCM
  ecc.py        # Reed-Solomon repair data
  pipeline.py   # encrypt, decrypt, check and repair DNA
  cli.py        # encrypt, decrypt, check and repair commands
tests/
  test_basic.py
  test_rot.py
  test_ecc.py
  test_integrity.py
main.py         # demo
```

## Limitations

- The DNA step is only an encoding. It is not a security feature, and the project is not a new cipher.
- A weak password is still weak. The strength of the encryption depends on the password.
- Repair fixes changed letters only. Added or lost letters cannot be repaired, and neither can damage above about 8 damaged bytes per 255-byte block.
- The checksum and repair data are public. They detect and fix accidents, but they do not stop someone who edits the DNA on purpose and recomputes them. Only the AES-GCM tag, which needs the password, catches that.
- The encoding never repeats a letter, but it does not balance GC content, and the DNA is about twice as long as the plain mapping.
- The checksum and repair data are public. They detect and fix accidents, but they do not stop someone who edits the DNA on purpose and recomputes them. Only the AES-GCM tag, which needs the password, catches that.
- This is a learning project and has not been security-audited. Do not use it to protect sensitive data.