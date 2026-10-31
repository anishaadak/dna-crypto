# dna-crypto

A small educational project that encrypts a message with a password and then writes the encrypted bytes as a DNA string (`A`, `C`, `G`, `T`). Decoding the DNA and supplying the same password gives the original message back.

The DNA part is only a fun way to **display and store** the result. The actual security comes from AES-256-GCM (see [Security](#security)).

## What it does

- **Encoding** (`dnacrypto/encoding.py`) — every byte is turned into 8 bits, and each pair of bits is mapped to one DNA letter: `00 → A`, `01 → C`, `10 → G`, `11 → T`. The reverse mapping restores the original bytes.
- **Encryption** (`dnacrypto/crypto.py`) — a password is stretched into a 32-byte key with scrypt, and the message is encrypted with AES-256-GCM. The output is `salt + nonce + ciphertext` (the GCM authentication tag is appended to the ciphertext).
- **CLI** (`dnacrypto/cli.py`) — `encrypt` and `decrypt` commands that prompt for the password without echoing it.
- **Demo** (`main.py`) — an interactive round trip: type a message and password, see the DNA, then see it decrypted again.

## Requirements

- Python 3.10 or newer
- [`cryptography`](https://pypi.org/project/cryptography/) (AES-GCM and scrypt)
- [`pytest`](https://pypi.org/project/pytest/) (only needed to run the tests)

## Install

```bash
pip install cryptography pytest
```

Using a virtual environment is recommended:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install cryptography pytest
```

## Run the demo

From the project root:

```bash
python main.py
```

It asks for a message and a password, then prints:

```
DNA: CAGACGGC...
Decrypted: your message
Match: True
```

For example:

```
Message: hello
Password: secret
DNA: ...
Decrypted: hello
Match: True
```

### Command line

The same functionality is available as a CLI:

```bash
python -m dnacrypto.cli encrypt --text "hello"
python -m dnacrypto.cli decrypt --dna "CAGACGGC..."
```

Both commands prompt for the password. (On Windows, `getpass` reads from the console, so you cannot pipe the password in.)

## Run the tests

```bash
python -m pytest
```

The tests cover the DNA encoding, a full byte round trip, successful decrypt, wrong-password rejection, and tamper detection.

## Security

**AES-256-GCM provides the security. DNA is only the way the encrypted result is written down.**

- The password is converted into a 32-byte key with **scrypt** (`n=2**15, r=8, p=1`). Scrypt is deliberately slow and memory-hungry, which makes guessing passwords expensive.
- A fresh random **16-byte salt** is generated for every encryption, so the same message and password never produce the same key or the same output twice.
- A fresh random **12-byte nonce** is generated for every encryption and must never repeat for a given key; generating it randomly per message is what keeps GCM safe here.
- **AES-256-GCM** encrypts the message and authenticates it. If the password is wrong or even one bit of the stored data is changed, decryption fails with `InvalidTag` instead of returning corrupted plaintext.
- The DNA step is a reversible 2-bits-per-letter encoding. It hides nothing and adds no cryptographic strength — the DNA string is exactly as sensitive as the raw ciphertext. Anyone with the DNA string and the password can decrypt it; anyone without the password cannot.

This is a learning project, not an audited security product. Choose a strong password, and treat the DNA output like any other ciphertext.
