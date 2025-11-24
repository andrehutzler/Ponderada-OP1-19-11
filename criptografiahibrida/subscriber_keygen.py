from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)

priv_pem = private_key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.TraditionalOpenSSL,
    serialization.NoEncryption()
)

with open("subscriber_private.pem", "wb") as f:
    f.write(priv_pem)

pub_pem = private_key.public_key().public_bytes(
    serialization.Encoding.PEM,
    serialization.PublicFormat.SubjectPublicKeyInfo
)

with open("subscriber_public.pem", "wb") as f:
    f.write(pub_pem)

print("Arquivos gerados: subscriber_private.pem e subscriber_public.pem")
