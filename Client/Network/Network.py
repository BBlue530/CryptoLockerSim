import platform
import subprocess
import re
import socket
import ipaddress
import concurrent.futures
import json
from Network.Scan_Device import load_ips_from_json, scan_local_ip_ports

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

def get_subnet_from_router(network_ip):
    try:
        network = ipaddress.IPv4Network(f'{network_ip}/24', strict=False)
        return str(network.network_address) + "/24"
    
    except ValueError as e:
        print(f"Error: {e}")
        return None

def get_hostname(ip):
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        hostname = ip
    return hostname

##############################################################################################################################################

# Simple ping to all machines within a netowrk and added routing to the pings so its more accurate
def scan_network(network_ip, massscan=False, timeout=2, verbose=False):
    devices = set()
    ip_prefix = ".".join(network_ip.split(".")[:3])
    router_ip = network_ip
    subnet = get_subnet_from_router(network_ip)

    def ping_device(ip):
        responded, ping_time = ping_ip(ip)
        if responded:   
            local_gateway = get_default_gateway()
            responding_device_network = get_target_network(ip)

            # If the responding devices network is the same as the network ip thats getting scanned
            if responding_device_network == network_ip:
                hostname = get_hostname(ip)
                devices.add((ip, hostname, ping_time))

            # In the case where its a local network scan so i wont have to comment out code
            elif local_gateway == network_ip:
                hostname = get_hostname(ip)
                devices.add((ip, hostname, ping_time))

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(ping_device, f"{ip_prefix}.{i}") for i in range(1, 254)]
        concurrent.futures.wait(futures)
    
    devices = list(devices)
    if massscan == False:
        if network_ip in devices:
            devices.remove(network_ip)
    return devices


def ping_ip(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if re.search(r"time=", result.stdout, re.IGNORECASE):
            match = re.search(r"time[=<]\s*(\d+)", result.stdout)
            if match:
                ping_time = match.group(1)
                return True, f"Time={ping_time}ms"

        if re.search(r"Destination host unreachable", result.stdout, re.IGNORECASE):
            return False

        if re.search(r"Request Timed Out", result.stdout, re.IGNORECASE):
            return False

        return False

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False
    
def get_target_network(target_ip):
    try:
        command = ["traceroute", target_ip] if platform.system() != "Windows" else ["tracert", target_ip]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"Error: {result.stderr.strip() or "Traceroute Failed. It Can Be Privilege issue"}"

        lines = result.stdout.split("\n")

        hops = []
        for line in lines:
            match = re.search(r"\[?(\d+\.\d+\.\d+\.\d+)\]?", line)
            if match:
                hops.append(match.group(1))

        # Gets the second to last hop in the traceroute since that will be the router/network ip
        if len(hops) >= 2:
            router_ip = hops[-2]
            return router_ip
        else:
            return "Unable to find IP."

    except Exception as e:
        return f"Error: {e}"

##############################################################################################################################################

def network_scan():
    # Get the default gateway
    default_gateway = get_default_gateway()
    if not default_gateway:
        return

    # Find the subnet
    subnet = get_subnet_from_router(default_gateway)
    if not subnet:
        return

    # Scan devices on the subnet
    devices = scan_network(default_gateway, massscan=False, timeout=2, verbose=True)

    # Prepare list for json
    devices_json = [
        {"ip": ip, "hostname": hostname, "ping": ping_time}
        for ip, hostname, ping_time in devices
    ]

    # Write json file
    output_filename = "network.json"
    with open(output_filename, "w") as f:
        json.dump(devices_json, f, indent=4)
    
    ips = load_ips_from_json(output_filename)
    results = scan_local_ip_ports(ips)
    
    # Save results inn json
    with open("ports_scan.json", "w") as f:
        json.dump(results, f, indent=4)

##############################################################################################################################################