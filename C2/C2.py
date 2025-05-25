from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from flask import request
import logging
import sys
import json
from datetime import datetime, timezone
from Extensions import limiter
# Imprting the blueprints here
from Routes.Key_Endpoints import key_bp
from Routes.JWT_Endpoints import jwt_bp
from Routes.Files_Endpoints import files_bp
from Routes.Payment_Endpoints import payments_bp
from Routes.Dashboard_Endpoints import dashboard_bp

####################################################################################################################

app = Flask(__name__)

limiter.init_app(app)

logging.getLogger('werkzeug').setLevel(logging.ERROR)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('log.json'), # This will pump out into .json file
        logging.StreamHandler(sys.stdout) # This will pump out into terminal
    ]
)

####################################################################################################################

app.register_blueprint(key_bp)
app.register_blueprint(jwt_bp)
app.register_blueprint(files_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(dashboard_bp)

####################################################################################################################

@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    return jsonify(error="rate limit exceeded"), 429

####################################################################################################################

@app.after_request # Need to find a better way to log
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
    logging.info(json.dumps(log_entry))
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