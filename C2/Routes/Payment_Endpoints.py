from flask import Blueprint, request, jsonify
import os
import sqlite3
from werkzeug.utils import secure_filename
import jwt
from C2_Variables import DB_PATH, KEY_STORAGE_DIR, jwt_key
from Validation import check_keys
from Extensions import limiter

payments_bp = Blueprint('payments', __name__)

####################################################################################################################

@payments_bp.route('/payment_status/<unique_id>', methods=['GET'])
@limiter.limit("5 per minute")
def payment_status(unique_id):
    received_api_key = request.headers.get('API-KEY')
    session_token = request.headers.get('Session-Token')
    unique_uuid = request.headers.get('uuid')
    received_ip = request.remote_addr
    decode_jwt = jwt.decode(session_token, jwt_key, algorithms=["HS256"])
    jwt_ip = decode_jwt.get("ip")
    jwt_uuid = decode_jwt.get("uuid")
    validation_failed = check_keys(received_api_key, session_token, jwt_ip, received_ip, unique_uuid, jwt_uuid)
    if validation_failed:
        return validation_failed
    
    unique_id_safe = secure_filename(unique_id)
    key_path = os.path.join(KEY_STORAGE_DIR, unique_id_safe)
    correct_key_path = os.path.realpath(key_path)
    if not correct_key_path.startswith(os.path.realpath(KEY_STORAGE_DIR)):
        return jsonify({"error": "File path"}), 400
    if not os.path.exists(correct_key_path):
        return jsonify({"error": "Filename not found"}), 404
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT paid FROM payments WHERE unique_id = ?', (unique_id,))
        result = c.fetchone()
        conn.close()

        if result is None:
            return jsonify({"error": "Unique ID not found"}), 404

        paid = bool(result[0])
        return jsonify({"unique_id": unique_id, "paid": paid}), 200
    except Exception as e:
        print(f"Error: {e}") # Debug Message
        return jsonify({"Error": "Error Happen"}), 500

####################################################################################################################