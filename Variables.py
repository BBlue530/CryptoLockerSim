import os

system_dirs = ["/bin", "/boot", "/dev", "/etc", "/lib", "/lib64", "/proc", "/run", "/sbin", "/sys", "/usr", "/var", "/tmp", os.path.expanduser("~/.config/autostart"), "/CryptoLockerSim"]
script_files = ["private.pem", "public.pem", "timer.json", "Main.py", "Timer.py", "Decrypt.py", "Encrypt.py", "key.encrypted", "Variables.py", "requirements.txt", "Move_File.py"]
system_desktop_dirs = system_dirs + [os.path.expanduser("~/.config/autostart"), "/CryptoLockerSim"]
script_name_exe = "Main.exe" # Change to what you have it named as
script_name_elf = "/home/kali/Desktop/CryptoLockerSim/Main.elf" # Currently hardcoded path but will change in the future
seconds_left = 600 # This variable will change the amount of time you have
password = "test"
timer_file_name = "timer.json"

c2_server = "http://51.20.137.153:5000" # Public IP from my EC2 instance
rsa_key = "private.pem"