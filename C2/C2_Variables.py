import os
from datetime import timedelta

####################################################################################################################

api_key = "12345"

seconds_left = 60

active_sessions = {}

session_token_expiration = timedelta(seconds = seconds_left)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_STORAGE_DIR = os.path.join(BASE_DIR, "keys")
DB_PATH = os.path.join(BASE_DIR, "payments.db")
os.makedirs(KEY_STORAGE_DIR, exist_ok=True)

####################################################################################################################