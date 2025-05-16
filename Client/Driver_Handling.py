import platform
import string
import os

def windows_drives():
    drives = []
    for drive_letter in string.ascii_uppercase:
        drive = f"{drive_letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def root_paths():
    if platform.system() == "Windows":
        return windows_drives()
    else:
        root_path = "/"
        return root_path