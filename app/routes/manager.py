from flask import Blueprint, session, redirect, url_for

manager = Blueprint('manager', __name__)

@manager.route('/manager_dashboard')
def manager_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return "Welcome to Manager Dashboard!"