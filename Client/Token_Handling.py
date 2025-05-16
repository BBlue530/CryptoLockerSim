from Session_Handling import read_session_token, read_unique_uuid
from Variables import api_key

def token_check():
    from RSA_Key_Handling import get_machine_identifier
    unique_id = get_machine_identifier()
    session_token = read_session_token()
    unique_uuid = read_unique_uuid()
    if session_token and unique_uuid:
        headers = {
        'API-KEY': api_key,
        'Session-Token' : session_token,
        'uuid' : unique_uuid
        }
    else:
        print("No session token or uuid") # Debug Message
        return
    
    renamed_key = f"{unique_id}_{unique_uuid}_private.pem"
    return headers, renamed_key, unique_id, unique_uuid