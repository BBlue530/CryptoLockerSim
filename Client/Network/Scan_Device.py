import socket
import json

##############################################################################################################################################

def load_ips_from_json(filename):
    with open(filename, "r") as f:
        devices = json.load(f)
    ips = [device["ip"] for device in devices if "ip" in device]
    return ips

##############################################################################################################################################

def banner_grab(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=2) as s:
            s.settimeout(2)
            return s.recv(1024).decode(errors="ignore").strip()
    except:
        return None

def scan_port(target_ip, port):
    try:
        with socket.create_connection((target_ip, port), timeout=1) as sock:
            banner = banner_grab(target_ip, port)
            result = {
                "Open_Port": f"Port: {port} is open IP: {target_ip} Banner: {banner}" if banner else f"Port: {port} is open IP: {target_ip}"
            }
            return result
    except (socket.timeout, socket.error):
        return None
    
def scan_local_ip_ports(ip_list, ports=[80, 443]):
    all_results = {}
    for ip in ip_list:
        open_ports = []
        for port in ports:
            res = scan_port(ip, port)
            if res:
                open_ports.append(res)
        if open_ports:
            all_results[ip] = open_ports
    return all_results

##############################################################################################################################################