'''
Example from: https://elc.github.io/python-security/chapters/07_Asymmetric_Encryption.html
'''
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

def generate_key_pair():
    key_size = 2048  # Should be at least 2048

    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )

    public_key = private_key.public_key()
    return private_key, public_key

private_key, public_key = generate_key_pair()

def encrypt(message, public_key):
    return public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

message = b"Hello World!"

message_encrypted = encrypt(message, public_key)

print(f"Encrypted Text: {message_encrypted.hex()}")

def decrypt(message_encrypted, private_key):
    try:
        message_decrypted = private_key.decrypt(
            message_encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return f"Decrypted Message: {message_decrypted}"
    except ValueError:
        return "Failed to Decrypt"
    
########ERROR - using other private key
private_key_other, _ = generate_key_pair()

message_decrypted = decrypt(message_encrypted, private_key_other)
print(message_decrypted)

########ERROR - using other puyblic key
_, public_key_other = generate_key_pair()

message_encrypted_other = encrypt(message, public_key_other)

message_decrypted = decrypt(message_encrypted_other, private_key)
print(message_decrypted)

#####Correct: Using original private key
message_decrypted = decrypt(message_encrypted, private_key)
print(message_decrypted)



###### Signing messages

def sign(message, private_key):
    return private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

message = b"My website is http://elc.github.io"

signature = sign(message, private_key)

print(f"Digital Signature: {signature.hex()}")

###### Verifyging siganture
def verify(signature, message, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return "The message has been successfully verified"
    except InvalidSignature:
        return "The signature, the message or the Public Key is invalid"
    
###### Verifying - wrong message (messaged changed)
wrong_message = b"My website is http://www.google.com"

verification_message = verify(signature, wrong_message, public_key)
print(verification_message)

####### Verifying - wrong mesage and singature (signature changed)
wrong_message = b"My website is http://www.google.com"

fake_private_key, _ = generate_key_pair()
fake_signature = sign(wrong_message, fake_private_key)

verification_message = verify(fake_signature, message, public_key)
print(verification_message)

####### Verifyigng - success if message and signature match
verification_message = verify(signature, message, public_key)
print(verification_message)



