import json
import base64
import os
import time
import paho.mqtt.client as mqtt

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "exemplo/hibrido/aes-rsa"

# Carrega chave pública do subscriber
with open("subscriber_public.pem", "rb") as f:
    subscriber_pub_pem = f.read()

subscriber_public_key = serialization.load_pem_public_key(subscriber_pub_pem)

def audit_print(title, data):
    print(f"\n===== {title} =====")
    print(data)

def encrypt_and_publish(plain_bytes):
    audit_print("Mensagem em texto puro", plain_bytes)

    # 1. Gerar chave AES-256
    aes_key = AESGCM.generate_key(bit_length=256)
    audit_print("Chave AES gerada (base64)", base64.b64encode(aes_key).decode())

    # 2. Nonce AES-GCM (12 bytes)
    nonce = os.urandom(12)
    audit_print("Nonce gerado (base64)", base64.b64encode(nonce).decode())

    # 3. Criptografar com AES-GCM
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(nonce, plain_bytes, None)
    audit_print("Ciphertext AES-GCM (base64)", base64.b64encode(ciphertext).decode())

    # 4. Encriptar a chave AES via RSA-OAEP
    encrypted_key = subscriber_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    audit_print("Chave AES cifrada com RSA-OAEP (base64)", base64.b64encode(encrypted_key).decode())

    # 5. Montar JSON
    payload = {
        "key_encrypted": base64.b64encode(encrypted_key).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }
    audit_print("Payload JSON pronto para envio", json.dumps(payload, indent=2))

    # 6. Envio MQTT
    result = client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
    audit_print("Status de publicação MQTT", str(result))

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

try:
    for i in range(2):
        msg = f"Mensagem secreta Nº{i} — {time.ctime()}".encode()
        encrypt_and_publish(msg)
        time.sleep(2)
finally:
    client.loop_stop()
    client.disconnect()
