from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
import os
import logging
import uuid
import json
import sys
from datetime import datetime, timezone, timedelta
import sqlite3
import threading
import time
import random

####################################################################################################################

app = Flask(__name__)

api_key = "12345"

seconds_left = 60

active_sessions = {}

session_token_expiration = timedelta(seconds = seconds_left)

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_STORAGE_DIR = os.path.join(BASE_DIR, "keys")
DB_PATH = os.path.join(BASE_DIR, "payments.db")
os.makedirs(KEY_STORAGE_DIR, exist_ok=True)

# Initialize the DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            unique_id TEXT PRIMARY KEY,
            btc_address TEXT,
            paid BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

####################################################################################################################

def check_expired_keys():
    while True:
        time.sleep(15)
        print("Checking for expired keys") # Debug Message
        expired_time = datetime.now(timezone.utc).timestamp() - seconds_left

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT unique_id, created_at FROM payments WHERE paid = 0')
        unpaid_keys = c.fetchall()

        for unique_id, created_at in unpaid_keys:
            if created_at is None:
                continue
            created_ts = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S").timestamp()
            if created_ts < expired_time:
                key_path = os.path.join(KEY_STORAGE_DIR, unique_id)
                if os.path.exists(key_path):
                    os.remove(key_path)
                c.execute('DELETE FROM payments WHERE unique_id = ?', (unique_id,)) # Removes expired keys
                print(f"{unique_id} Expired")
        
        conn.commit()
        conn.close()

def start_remove_expired_keys():
    thread = threading.Thread(target=check_expired_keys)
    thread.daemon = True
    thread.start()

start_remove_expired_keys()

####################################################################################################################
# This will just simulate mock payment
def mock_payment():
    while True:
        time.sleep(60)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT unique_id FROM payments WHERE paid = 0')
        unpaid = c.fetchall()

        for row in unpaid:
            unique_id = row[0]
            btc_received = random.uniform(0.004, 0.008)  # Random amount transfered for testing
            print(f"Received: {unique_id}: {btc_received:.6f} BTC")

            if btc_received >= 0.005:  # When btc_received is 0.005
                c.execute('UPDATE payments SET paid = 1 WHERE unique_id = ?', (unique_id,))
                print(f"Marked {unique_id} as PAID")
        
        conn.commit()
        conn.close()

def start_mock_payment():
    thread = threading.Thread(target=mock_payment)
    thread.daemon = True
    thread.start()

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