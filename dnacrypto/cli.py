import argparse
import getpass

from cryptography.exceptions import InvalidTag

from dnacrypto.pipeline import (
    check_dna,
    decrypt_from_dna,
    encrypt_to_dna,
    repair_dna,
)


def encrypt_command(args) -> int:
    password = getpass.getpass("Password: ")
    dna = encrypt_to_dna(args.text, password)
    print(dna)
    return 0


def decrypt_command(args) -> int:
    dna = args.dna
    password = getpass.getpass("Password: ")
    try:
        message = decrypt_from_dna(dna, password)
    except ValueError:
        print("That DNA is damaged beyond repair, or not valid. Run the check command to see why.")
        return 1
    except InvalidTag:
        print("Wrong password, or the data was changed.")
        return 1
    print(message)
    return 0


def repair_command(args) -> int:
    dna = args.dna
    try:
        fixed, positions = repair_dna(dna)
    except ValueError:
        print("Too damaged to repair, or not valid DNA. Run the check command to see why.")
        return 1
    if positions:
        print("Fixed {} damaged byte(s).".format(len(positions)))
    else:
        print("No damage found.")
    print(fixed)
    if args.out:
        with open(args.out, "w") as f:
            f.write(fixed)
    return 0


def check_command(args) -> int:
    dna = args.dna
    password = getpass.getpass("Password: (leave empty to skip) ")
    if password == "":
        password = None
    status, message = check_dna(dna, password)
    print(status.upper())
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

    repair_parser = subparsers.add_parser("repair")
    repair_parser.add_argument("--dna", required=True)
    repair_parser.add_argument("--out")
    repair_parser.set_defaults(func=repair_command)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--dna", required=True)
    check_parser.set_defaults(func=check_command)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
