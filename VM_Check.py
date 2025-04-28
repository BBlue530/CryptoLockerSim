import os
import platform
import subprocess

def running_in_vm():
    system = platform.system()

    # CPU flag check for hypervisor on linux
    if system == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                if "hypervisor" in f.read().lower():
                    return True
        except FileNotFoundError:
            pass
        # Check for vm vendor strings
        dmi_files = [
            "/sys/class/dmi/id/product_name",
            "/sys/class/dmi/id/product_version",
            "/sys/class/dmi/id/sys_vendor",
        ]
        vm_indicators = ["virtual", "vmware", "qemu", "kvm", "xen", "microsoft", "parallels", "bhyve"]
        for path in dmi_files:
            if os.path.exists(path):
                try:
                    text = open(path, "r").read().lower()
                    if any(ind in text for ind in vm_indicators):
                        return True
                except Exception:
                    pass
    # Check for WMI if its on metal or vm
    elif system == "Windows":
        try:
            output = subprocess.check_output(
                ["wmic", "computersystem", "get", "model"],
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            ).decode(errors="ignore").lower()
            if any(ind in output for ind in ["virtual", "vmware", "virtualbox", "kvm", "qemu", "hyper-v", "xen"]):
                return True
        except Exception:
            pass
    return False