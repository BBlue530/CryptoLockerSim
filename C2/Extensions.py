from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from C2_Variables import blocked_ips, rate_limit_counter, rate_limit_threshold

####################################################################################################################

limiter = Limiter(key_func=get_remote_address, default_limits=[])

####################################################################################################################

def update_block_ip_list(ip):
    rate_limit_counter[ip] += 1
    if rate_limit_counter[ip] >= rate_limit_threshold:
        blocked_ips.add(ip)

####################################################################################################################