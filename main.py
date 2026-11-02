from dnacrypto.encoding import gc_content, longest_run
from dnacrypto.pipeline import (
    check_dna,
    damage_letter,
    decrypt_from_dna,
    encrypt_to_dna,
    repair_dna,
)

message = input("Message: ")
password = input("Password: ")

# lock it, then write it as DNA
dna = encrypt_to_dna(message, password)
print("DNA:", dna)
print("Length:", len(dna))
print("Longest run of the same letter:", longest_run(dna))
print("GC content: {:.1f}%".format(gc_content(dna) * 100))

# read the DNA back, then unlock it
result = decrypt_from_dna(dna, password)
print("Decrypted:", result)
print("Match:", result == message)

if len(dna) > 100:
    print("Now damaging letter 100 on purpose...")
    damaged = damage_letter(dna, 100)
    status, _ = check_dna(damaged)
    print(status)
    fixed, positions = repair_dna(damaged)
    print("Repaired DNA matches the original:", fixed == dna)