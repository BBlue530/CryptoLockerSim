import os
import platform
import subprocess
from Variables import dmi_files, vm_indicators, vm_mac_prefixes

def running_in_vm():
    system = platform.system()

    if system == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                if "hypervisor" in f.read().lower():
                    return True
        except:
            pass
        
        for path in dmi_files:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        if any(ind in f.read().lower() for ind in vm_indicators):
                            return True
                except:
                    pass

    elif system == "Windows":
        try:
            for command in [["wmic", "computersystem", "get", "model"],
                            ["wmic", "bios", "get", "manufacturer"],
                            ["wmic", "baseboard", "get", "manufacturer"]]:
                output = subprocess.check_output(command, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL).decode(errors="ignore").lower()
                if any(ind in output for ind in vm_indicators):
                    return True
        except:
            pass

    try:
        import uuid
        mac = uuid.getnode()
        mac_str = ':'.join(['{:02x}'.format((mac >> ele) & 0xff) for ele in range(40, -1, -8)])
        if any(mac_str.startswith(prefix) for prefix in vm_mac_prefixes):
            return True
    except:
        pass
    return False