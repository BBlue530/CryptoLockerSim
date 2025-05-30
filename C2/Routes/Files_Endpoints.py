from flask import Blueprint, request, jsonify, send_file
import os
import random
import sqlite3
from werkzeug.utils import secure_filename
import jwt
from C2_Variables import DB_PATH, KEY_STORAGE_DIR, FILE_STORAGE_DIR, extesions, jwt_key
from Validation import check_keys
from Extensions import limiter, update_block_ip_list, check_uploaded_file

files_bp = Blueprint('files', __name__)

####################################################################################################################

@files_bp.route('/upload_file', methods=['POST']) 
def upload_file():
    received_api_key = request.headers.get('API-KEY')
    session_token = request.headers.get('Session-Token')
    unique_uuid = request.headers.get('uuid')
    received_ip = request.remote_addr
    validation_failed = check_keys(received_api_key, session_token, received_ip, unique_uuid)
    if validation_failed:
        return validation_failed

    uploaded_file = request.files.get('file')
    validation_result = check_uploaded_file(uploaded_file)
    if validation_result:
        return validation_result

    key_filename = secure_filename(uploaded_file.filename)
    
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