from flask import Flask, request, jsonify, send_file
import os
import sqlite3
import threading
import time
import random

####################################################################################################################

app = Flask(__name__)

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
            paid BOOLEAN DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

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

@app.route('/upload_key', methods=['POST'])
def upload_key():
    key_file = request.files.get('key')
    if not key_file:
        return jsonify({"error": "No key provided"}), 400 # Debug Message

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

####################################################################################################################