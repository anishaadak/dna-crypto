from dnacrypto.encoding import (
    bytes_to_dna_safe,
    dna_to_bytes_safe,
    gc_content,
    longest_run,
)
from dnacrypto.crypto import lock, unlock

message = input("Message: ")
password = input("Password: ")

# lock it, then write it as DNA
dna = bytes_to_dna_safe(lock(message, password))
print("DNA:", dna)
print("Length:", len(dna))
print("Longest run of the same letter:", longest_run(dna))
print("GC content: {:.1f}%".format(gc_content(dna) * 100))

# read the DNA back, then unlock it
result = unlock(dna_to_bytes_safe(dna), password)
print("Decrypted:", result)
print("Match:", result == message)