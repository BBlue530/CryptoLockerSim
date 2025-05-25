from flask import Blueprint, request, jsonify
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from C2_Variables import api_key, seconds_left, jwt_key, KEY_STORAGE_DIR, DB_PATH
from Extensions import limiter

jwt_bp = Blueprint('jwt', __name__)

####################################################################################################################

@jwt_bp.route('/create_session', methods=['POST'])
@limiter.limit("1 per minute")
def create_jwt_session():
    try:
        received_api_key = request.headers.get('API-KEY')
        if received_api_key != api_key:
            return jsonify({"error": "Invalid API Key"}), 403

        expiration = datetime.now(timezone.utc) + timedelta(seconds = seconds_left)
        unique_uuid = str(uuid.uuid4())
        payload = {
            "exp": expiration,
            "iat": datetime.now(timezone.utc).timestamp(),
            "ip": request.remote_addr,
            "uuid": unique_uuid
        }
        session_token = jwt.encode(payload, jwt_key, algorithm="HS256")

        return jsonify({"session_token": session_token, "uuid": unique_uuid})
    except Exception as e:
        print(f"Error: {e}") # Debug Message
        return jsonify({"Error": "Error Happen"}), 500

####################################################################################################################