import argparse
import getpass

from cryptography.exceptions import InvalidTag

from dnacrypto.crypto import lock, unlock
from dnacrypto.encoding import bytes_to_dna, dna_to_bytes

VALID_DNA = {"A", "C", "G", "T"}


def is_valid_dna(dna: str) -> bool:
    return bool(dna) and all(letter in VALID_DNA for letter in dna)


def encrypt_command(args) -> int:
    password = getpass.getpass("Password: ")
    dna = bytes_to_dna(lock(args.text, password))
    print(dna)
    return 0


def decrypt_command(args) -> int:
    dna = args.dna
    if not is_valid_dna(dna):
        print("That is not valid DNA.")
        return 1
    password = getpass.getpass("Password: ")
    try:
        message = unlock(dna_to_bytes(dna), password)
    except InvalidTag:
        print("Wrong password, or the data was changed.")
        return 1
    print(message)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dnacrypto")
    subparsers = parser.add_subparsers(dest="command", required=True)

    encrypt_parser = subparsers.add_parser("encrypt")
    encrypt_parser.add_argument("--text", required=True)
    encrypt_parser.set_defaults(func=encrypt_command)

    decrypt_parser = subparsers.add_parser("decrypt")
    decrypt_parser.add_argument("--dna", required=True)
    decrypt_parser.set_defaults(func=decrypt_command)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
