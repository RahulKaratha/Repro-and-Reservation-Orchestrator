from flask import Blueprint, render_template, session, redirect, url_for
from app.models.workgroupAssignment import WorkgroupAssignment
from app.models.workgroup import Workgroup
from app.extensions import db

engineer = Blueprint('engineer', __name__)


@engineer.route('/engineer_dashboard')
def engineer_dashboard():

    # Check login
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Get engineer workgroup assignments
    assignments = (
        db.session.query(Workgroup)
        .join(WorkgroupAssignment, Workgroup.id == WorkgroupAssignment.workgroup_id)
        .filter(WorkgroupAssignment.employee_id == user_id)
        .all()
    )

    assigned_count = len(assignments)

    return render_template(
        "engineer_dashboard.html",
        assignments=assignments,
        assigned_count=assigned_count
    )