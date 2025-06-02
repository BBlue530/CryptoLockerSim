from flask import Blueprint, request, jsonify, render_template, make_response
import jwt
from datetime import datetime, timedelta, timezone
from C2_Variables import jwt_key_dashboard, jwt_expire_dashboard, username, password
from Extensions import limiter

login_bp = Blueprint('login', __name__)

####################################################################################################################

@login_bp.route('/dashboard/login', methods=['GET'])
@limiter.limit("10 per minute")
def login_page():
    return render_template('Dashboard_Login.html')

@login_bp.route('/dashboard/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    data = request.get_json()
    given_username = data.get("username")
    given_password = data.get("password")

    if given_username == username and given_password == password:
        expiration = datetime.now(timezone.utc) + timedelta(seconds=jwt_expire_dashboard)
        payload = {
            "user": given_username,
            "role": "admin",
            "exp": expiration,
            "iat": datetime.now(timezone.utc).timestamp()
        }
        token = jwt.encode(payload, jwt_key_dashboard, algorithm="HS256")

        response = make_response(jsonify({"message": "Login"}))
        response.set_cookie(
            'token',
            token,
            httponly=True,
            samesite='Lax',
            max_age=jwt_expire_dashboard
        )
        return response, 200
    else:
        return jsonify({"error": "Invalid Login"}), 401
    
####################################################################################################################