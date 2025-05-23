import os
import platform
import subprocess
import cpuinfo
from Core.Variables import dmi_files, vm_indicators, vm_mac_prefixes

def running_in_vm():
    system = platform.system()

    if system == "Linux":
        if hypervisor_check():
            print("hypervisor triggered vm") # Debug Message
            return True
        if dmi_file_check():
            print("dmi file triggered vm") # Debug Message
            return True
        if mac_address_check():
            print("mac address triggered vm") # Debug Message
            return True

    elif system == "Windows":
        if hypervisor_check():
            print("hypervisor triggered vm") # Debug Message
            return True
        if wmic_check():
            print("wmic triggered vm") # Debug Message
            return True
        if dmi_file_check():
            print("dmi file triggered vm") # Debug Message
            return True
        if mac_address_check():
            print("mac address triggered vm") # Debug Message
            return True

    return False

####################################################################################################################

# Checks for linux VM
def hypervisor_check():
    try:
        info = cpuinfo.get_cpu_info()
        if "hypervisor" in info.get("flags", []):
            return True
    except:
        pass
    return False


def dmi_file_check():
    for path in dmi_files:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    if any(ind in f.read().lower() for ind in vm_indicators):
                        return True
            except:
                pass
    return False

####################################################################################################################

# Checks for windows VM
def wmic_check():
    try:
        for command in [["wmic", "computersystem", "get", "model"],
                        ["wmic", "bios", "get", "manufacturer"],
                        ["wmic", "baseboard", "get", "manufacturer"]]:
            output = subprocess.check_output(command, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode(errors="ignore").lower()
            if any(ind in output for ind in vm_indicators):
                return True
    except:
        pass
    return False

####################################################################################################################

# Checks for windows/linux VM
def mac_address_check():
    try:
        import uuid
        mac = uuid.getnode()
        mac_str = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(40, -1, -8)])
        if any(mac_str.startswith(prefix) for prefix in vm_mac_prefixes):
            return True
    except:
        pass
    return False

####################################################################################################################