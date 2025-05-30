from flask import Blueprint, render_template
import sqlite3
from datetime import datetime, timezone
import json
import os
from Extensions import limiter
from C2_Variables import DB_PATH, seconds_left, dashboard_log_json, c2_log_json

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
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', f'{dashboard_log_json}'))
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
        data.reverse()
        pretty_json = json.dumps(data, indent=4)
    except Exception as e:
        pretty_json = f"Error loading json: {e}"

    return render_template('Dashboard_Log.html', log_data=pretty_json)

####################################################################################################################

@dashboard_bp.route('/dashboard/log/c2')
def dashboard_log_c2():
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', f'{c2_log_json}'))
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
        data.reverse()
        pretty_json = json.dumps(data, indent=4)
    except Exception as e:
        pretty_json = f"Error loading json: {e}"

    return render_template('Dashboard_Log.html', log_data=pretty_json)

####################################################################################################################

@dashboard_bp.route('/dashboard/payments')
def dashboard_log_payments():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM payments ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()

    payments = []
    for row in rows:
        time_left = None
        if row['created_at'] and not row['paid']:
            try:
                created_at = datetime.strptime(row['created_at'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                expires_at = created_at.timestamp() + seconds_left
                time_now = datetime.now(timezone.utc).timestamp()
                time_left = max(0, int(expires_at - time_now))
            except:
                time_left = None

        payments.append({
            "unique_id": row["unique_id"],
            "btc_address": row["btc_address"],
            "paid": row["paid"],
            "created_at": row["created_at"],
            "time_left": time_left
        })

    return render_template('Dashboard_Payments.html', log_data=payments)

####################################################################################################################