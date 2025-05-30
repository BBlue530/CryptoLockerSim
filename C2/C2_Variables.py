import os
from collections import defaultdict

####################################################################################################################

api_key = "12345"

seconds_left = 660

jwt_key = "Test Key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_STORAGE_DIR = os.path.join(BASE_DIR, "keys")
DB_PATH = os.path.join(BASE_DIR, "payments.db")
os.makedirs(KEY_STORAGE_DIR, exist_ok=True)

FILE_STORAGE_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILE_STORAGE_DIR, exist_ok=True)

####################################################################################################################

extesions = ['.test', '.xd']

####################################################################################################################

dashboard_log_json = 'dashboard_log.json'
c2_log_json = 'c2_log.json'

####################################################################################################################

blocked_ips = set()
rate_limit_counter = defaultdict(int)
rate_limit_threshold = 3

####################################################################################################################