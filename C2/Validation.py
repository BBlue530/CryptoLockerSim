from flask import request, jsonify
import jwt
from C2_Variables import api_key, jwt_key

def check_keys(received_api_key, session_token):
    if not received_api_key:
        return jsonify({"error": "Missing API Key"}), 401
    if not session_token:
        return jsonify({"error": "Missing session token"}), 401
    
    if received_api_key != api_key:
        return jsonify({"error": "Invalid API Key"}), 403
    
    try:
        payload = jwt.decode(session_token, jwt_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Session token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid session token"}), 401
    return None