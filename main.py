from dnacrypto.encoding import gc_content, longest_run
from dnacrypto.pipeline import decrypt_from_dna, encrypt_to_dna

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