import argparse
import getpass

from dnacrypto.encoding import bytes_to_dna, dna_to_bytes
from dnacrypto.crypto import lock, unlock


def encrypt(text: str) -> str:
    # ask for the password, then lock it and turn the result into DNA
    password = getpass.getpass("Password: ")
    return bytes_to_dna(lock(text, password))


def decrypt(dna: str) -> str:
    # ask for the password, turn the DNA back into bytes, then unlock it
    password = getpass.getpass("Password: ")
    return unlock(dna_to_bytes(dna), password)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dnacrypto", description="Encrypt and decrypt messages as DNA.")
    commands = parser.add_subparsers(dest="command", required=True)

    encrypt_cmd = commands.add_parser("encrypt", help="encrypt a message into DNA")
    encrypt_cmd.add_argument("--text", required=True, help="the message to encrypt")

    decrypt_cmd = commands.add_parser("decrypt", help="decrypt DNA back into a message")
    decrypt_cmd.add_argument("--dna", required=True, help="the DNA string to decrypt")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "encrypt":
        print(encrypt(args.text))
    else:
        print(decrypt(args.dna))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
