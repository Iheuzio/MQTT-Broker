from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


def generate_key_pair(password):
    key_size = 2048  # Should be at least 2048
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )
    public_key = private_key.public_key()

    #######Storing private key

    key_pem_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,  # PEM Format is specified
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(password),
    )

    # Filename could be anything
    key_pem_path = Path("keys/private.pem")
    key_pem_path.write_bytes(key_pem_bytes)
    print("private key saved to keys/private.pem")

    ###### Storing public key
    public_key = private_key.public_key()

    public_pem_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Filename could be anything
    public_pem_path = Path("keys/public.pem")
    public_pem_path.write_bytes(public_pem_bytes)
    print("public key saved to keys/private.pem")

def load_keys(password):
    private_pem_bytes = Path("keys/private.pem").read_bytes()
    public_pem_bytes = Path("keys/public.pem").read_bytes()

    try:
        private_key_from_pem = serialization.load_pem_private_key(
            private_pem_bytes,
            password=password,
        )
        public_key_from_pem = serialization.load_pem_public_key(public_pem_bytes)
        print("Keys Correctly Loaded")
        return private_key_from_pem, public_key_from_pem
    except ValueError:
        print("Incorrect Password")

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
        return True
    except InvalidSignature:
        return False