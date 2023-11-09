'''
Example from: https://elc.github.io/python-security/chapters/06_Symmetric_Encryption.html
'''

import secrets
import cryptography
import pytest

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

message = b"Hello World!"

key = secrets.token_bytes(32) # 16, 24, or 32
nonce = secrets.token_bytes(24)

#AES + GCM - Symetric encryption + authentication
ciphered_message = AESGCM(key).encrypt(nonce, message, None)

encrypted_message = f"{nonce.hex()}:{ciphered_message.hex()}"

print(f"Secret Key: {key.hex()}")
print(f"Public Nonce: {nonce.hex()}")
print(f"Encrypted Message: {encrypted_message}")


###################### Decrypt
def verify(password, nonce, message):
    try:
        decrypted_message = AESGCM(password).decrypt(nonce, message, None)
        return f"Decrypted Message: {decrypted_message}"
    except cryptography.exceptions.InvalidTag:
        return "Verification Failed - Either the message has been altered or the nonce or key are incorrect"


##################### Decrypt - Wrong key
guess_password = bytes.fromhex("1329f363a87306c33952a7cbfc0ebf8105126764d1c72c511031a5b028110cf9")

nonce, ciphered_message = encrypted_message.split(":")
nonce_bytes = bytes.fromhex(nonce)
ciphered_message_bytes = bytes.fromhex(ciphered_message)

print(verify(guess_password, nonce_bytes, ciphered_message_bytes))

################## Decrypt - Right key
nonce, ciphered_message = encrypted_message.split(":")
nonce_bytes = bytes.fromhex(nonce)
ciphered_message_bytes = bytes.fromhex(ciphered_message)

print(verify(key, nonce_bytes, ciphered_message_bytes))