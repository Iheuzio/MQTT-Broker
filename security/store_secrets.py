'''
Example from: https://elc.github.io/python-security/chapters/07_Asymmetric_Encryption.html

Note: NEVER upload private key files to source control, make sure to 
add the file to your .gitignore

'''

from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

def generate_key_pair():
    key_size = 2048  # Should be at least 2048

    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )

    public_key = private_key.public_key()
    return private_key, public_key
private_key, public_key = generate_key_pair()


#######Storing private key

password = b"my secret"

key_pem_bytes = private_key.private_bytes(
   encoding=serialization.Encoding.PEM,  # PEM Format is specified
   format=serialization.PrivateFormat.PKCS8,
   encryption_algorithm=serialization.BestAvailableEncryption(password),
)

# Filename could be anything
key_pem_path = Path("key.pem")
key_pem_path.write_bytes(key_pem_bytes);

warning_message = "\n\n     TRUNCATED CONTENT TO REMIND THIS SHOULD NOT BE SHARED\n"

content = key_pem_path.read_text()
content = content[:232] + warning_message + content[1597:]

print(content)

###### Storing public key
public_key = private_key.public_key()

public_pem_bytes = public_key.public_bytes(
   encoding=serialization.Encoding.PEM,
   format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# Filename could be anything
public_pem_path = Path("public.pem")
public_pem_path.write_bytes(public_pem_bytes);

public_key_content = public_pem_path.read_text()
print(public_key_content)

################ Loading keys
########## Incorrectr password
private_pem_bytes = Path("key.pem").read_bytes()
public_pem_bytes = Path("public.pem").read_bytes()

guess_password = b"my pass"

try:
    private_key_from_pem = serialization.load_pem_private_key(
        private_pem_bytes,
        password=guess_password,
    )
    public_key_from_pem = serialization.load_pem_public_key(public_pem_bytes)
    print("Keys Correctly Loaded")
except ValueError:
    print("Incorrect Password")

####### Right password
private_pem_bytes = Path("key.pem").read_bytes()
public_pem_bytes = Path("public.pem").read_bytes()

try:
    private_key_from_pem = serialization.load_pem_private_key(
        private_pem_bytes,
        password=password,
    )
    public_key_from_pem = serialization.load_pem_public_key(public_pem_bytes)
    print("Keys Correctly Loaded")
except ValueError:
    print("Incorrect Password")