import argparse
import getpass

from cryptography.exceptions import InvalidTag

from dnacrypto.crypto import lock, unlock
from dnacrypto.encoding import bytes_to_dna_safe, dna_to_bytes_safe


def encrypt_command(args) -> int:
    password = getpass.getpass("Password: ")
    dna = bytes_to_dna_safe(lock(args.text, password))
    print(dna)
    return 0


def decrypt_command(args) -> int:
    dna = args.dna
    password = getpass.getpass("Password: ")
    try:
        message = unlock(dna_to_bytes_safe(dna), password)
    except ValueError:
        print("That is not valid DNA.")
        return 1
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
