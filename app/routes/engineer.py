from flask import Blueprint, session, redirect, url_for

engineer = Blueprint('engineer', __name__)

@engineer.route('/engineer_dashboard')
def engineer_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return "Welcome to Engineer Dashboard!"