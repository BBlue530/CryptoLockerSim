from flask import Blueprint, render_template
from Extensions import limiter

dashboard_bp = Blueprint('dashboard', __name__)

####################################################################################################################

@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template('Dashboard_Home.html')

####################################################################################################################