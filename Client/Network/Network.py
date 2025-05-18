import platform
import subprocess
import re
import concurrent.futures
from Network.Scan_Device import scan_ips_ports

##############################################################################################################################################

def get_default_gateway():
    try:
        if platform.system() == "Windows":
            command = ["route", "print"]
        else:
            command = ["ip", "route"] if platform.system() != "Darwin" else ["netstat", "-rn"]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return None

        lines = result.stdout.split("\n")
        for line in lines:
            if platform.system() == "Windows":
                # Windows parsing
                match = re.search(r"0\.0\.0\.0\s+0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", line)
            else:
                # Linux/Mac parsing
                match = re.search(r"default\s+via\s+(\d+\.\d+\.\d+\.\d+)", line) or \
                        re.search(r"0\.0\.0\.0\s+(\d+\.\d+\.\d+\.\d+)", line)

            if match:
                return match.group(1)

        return None

    except Exception:
        return None

##############################################################################################################################################

# Simple ping to all machines within a netowrk and added routing to the pings so its more accurate
def scan_network(ports):
    # Get the default gateway
    network_ip = get_default_gateway()
    if not network_ip:
        return
    ip_prefix = ".".join(network_ip.split(".")[:3])

    def ping_device(ip, ports):
        responded = ping_ip(ip)
        if responded:   
            # If the responding devices network is the same as the network ip thats getting scanned
            scan_ips_ports(ip, ports)

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(ping_device, f"{ip_prefix}.{i}", ports) for i in range(1, 254)]
        concurrent.futures.wait(futures)


def ping_ip(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if re.search(r"time=", result.stdout, re.IGNORECASE):
            match = re.search(r"time[=<]\s*(\d+)", result.stdout)
            if match:
                ping_time = match.group(1)
                return True

        if re.search(r"Destination host unreachable", result.stdout, re.IGNORECASE):
            return False

        if re.search(r"Request Timed Out", result.stdout, re.IGNORECASE):
            return False

        return False

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

##############################################################################################################################################