import os

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