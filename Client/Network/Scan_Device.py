import socket

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
        if banner == "Random Bannner":
            print(f"{target_ip} Banner: Random Bannner {banner}") # I can add a method here to do something if the condition is met
        else:
            pass
        if port == 80:
            print(f"{target_ip} Port Open: {port}") # I can add a method here to do something if the condition is met
        else:
            pass
        if port == 443:
            print(f"{target_ip} Port Open: {port}") # I can add a method here to do something if the condition is met
        else:
            pass
        return
    except (socket.timeout, socket.error):
        return None
    
def scan_ips_ports(ip, ports):
        for port in ports:
            scan_port(ip, port)

##############################################################################################################################################