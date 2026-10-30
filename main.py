from dnacrypto.encoding import bytes_to_dna, dna_to_bytes
from dnacrypto.crypto import lock, unlock

message = input("Message: ")
password = input("Password: ")

# lock it, then write it as DNA
dna = bytes_to_dna(lock(message, password))
print("DNA:", dna)

# read the DNA back, then unlock it
result = unlock(dna_to_bytes(dna), password)
print("Decrypted:", result)
print("Match:", result == message)