from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify, redirect, render_template
from werkzeug.utils import secure_filename
import jwt
from C2_Variables import blocked_ips, rate_limit_counter, rate_limit_threshold, extesions, jwt_key_dashboard

####################################################################################################################

limiter = Limiter(key_func=get_remote_address, default_limits=[])

####################################################################################################################

def update_block_ip_list(ip):
    rate_limit_counter[ip] += 1
    if rate_limit_counter[ip] >= rate_limit_threshold:
        blocked_ips.add(ip)

####################################################################################################################

def check_uploaded_file(uploaded_file):
    if not uploaded_file:
        return jsonify({"error": "No file provided"}), 400

    filename = secure_filename(uploaded_file.filename)
    filename_lower = filename.lower()
    parts = filename_lower.split('.')

    if len(parts) == 1:
        return jsonify({"error": "No file extension found"}), 400

    # Checks for any extensions inside of the name
    for ext_part in parts[1:]:
        ext = '.' + ext_part
        if ext not in extesions:
            return jsonify({"error": "File type not allowed"}), 400

    return None

####################################################################################################################

def check_pem_file(uploaded_file):
    uploaded_filename = uploaded_file.filename
    uploaded_filename_lower = uploaded_filename.lower()
    parts = uploaded_filename_lower.split('.')

    if len(parts) == 1:
        return False, "No file extension found"

    # Checks for any extensions inside of the name
    for part in parts[1:]:
        ext = '.' + part
        if ext != '.pem':
            return False, "File type not allowed"

    return True, None
    
####################################################################################################################

def check_token(token, web_page):

    if not token:
        return redirect('/dashboard/login')
    
    try:
        payload = jwt.decode(token, jwt_key_dashboard, algorithms=["HS256"])
        role = payload.get("role")
        if role != "admin":
            return redirect('/dashboard/login')
        
        return render_template(web_page)
    
    except jwt.ExpiredSignatureError:
        return redirect('/dashboard/login')
    
    except jwt.InvalidTokenError:
        return redirect('/dashboard/login')
    
####################################################################################################################

def check_token_log(token, web_page, log_data):

    if not token:
        return redirect('/dashboard/login')
    
    try:
        payload = jwt.decode(token, jwt_key_dashboard, algorithms=["HS256"])
        role = payload.get("role")
        if role != "admin":
            return redirect('/dashboard/login')
        
        return render_template(web_page, log_data=log_data)
    
    except jwt.ExpiredSignatureError:
        return redirect('/dashboard/login')
    
    except jwt.InvalidTokenError:
        return redirect('/dashboard/login')
    
####################################################################################################################