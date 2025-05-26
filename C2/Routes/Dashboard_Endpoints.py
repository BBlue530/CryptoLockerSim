from flask import Blueprint, render_template
import json
import os
from Extensions import limiter

dashboard_bp = Blueprint('dashboard', __name__)

####################################################################################################################

@dashboard_bp.route('/dashboard/home')
def dashboard_home():
    return render_template('Dashboard_Home.html')

####################################################################################################################

@dashboard_bp.route('/dashboard/log')
def dashboard_log():
    return render_template('Dashboard_Log.html')

####################################################################################################################

@dashboard_bp.route('/dashboard/log/dashboard')
def dashboard_log_dashboard():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dashboard_log.json'))
    data = []
    try:
        with open(json_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    data.append(obj)
                except json.JSONDecodeError:
                    pass
        pretty_json = json.dumps(data, indent=4)
    except Exception as e:
        pretty_json = f"Error loading log.json: {e}"

    return render_template('Dashboard_Log.html', log_data=pretty_json)

####################################################################################################################

@dashboard_bp.route('/dashboard/log/c2')
def dashboard_log_c2():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'c2_log.json'))
    data = []
    try:
        with open(json_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    data.append(obj)
                except json.JSONDecodeError:
                    pass
        pretty_json = json.dumps(data, indent=4)
    except Exception as e:
        pretty_json = f"Error loading log.json: {e}"

    return render_template('Dashboard_Log.html', log_data=pretty_json)

####################################################################################################################