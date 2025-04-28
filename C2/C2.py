from flask import Flask, request, jsonify, send_file
import os

####################################################################################################################

app = Flask(__name__)

# Makes the key directory absolute
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_STORAGE_DIR = os.path.join(BASE_DIR, "keys")
os.makedirs(KEY_STORAGE_DIR, exist_ok=True)

####################################################################################################################

@app.route('/upload_key', methods=['POST'])
def upload_key():
    key_file = request.files.get('key')
    if not key_file:
        return jsonify({"error": "No key provided"}), 400 # Debug Message

    key_filename = key_file.filename
    key_path = os.path.join(KEY_STORAGE_DIR, key_filename)

    try:
        key_file.save(key_path)
        return jsonify({"message": "Key uploaded", "file": key_filename}), 200 # Debug Message
    except Exception as e:
        return jsonify({"error": str(e)}), 500 # Debug Message

####################################################################################################################

@app.route('/get_key/<unique_id>', methods=['GET'])
def get_key(unique_id):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

####################################################################################################################