from flask import request, jsonify
import jwt
from C2_Variables import api_key, jwt_key

def check_keys(received_api_key, session_token, jwt_ip, received_ip, unique_uuid, jwt_uuid):
    print(f"jwt_ip: {jwt_ip}") # Debug Message
    print(f"received_ip: {received_ip}") # Debug Message
    print(f"unique_uuid: {unique_uuid}") # Debug Message
    print(f"jwt_uuid: {jwt_uuid}") # Debug Message
    if jwt_ip != received_ip:
        return jsonify({"error": "IP mismatch"}), 403
    if unique_uuid != jwt_uuid:
        return jsonify({"error": "uuid mismatch"}), 403
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