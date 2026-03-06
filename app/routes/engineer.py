from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment

engineer = Blueprint("engineer", __name__)


@engineer.route("/engineer/dashboard")
def engineer_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    engineer_id = session["user_id"]

    current_user = User.query.get(engineer_id)

    assignments = WorkgroupAssignment.query.filter_by(
        employee_id=engineer_id
    ).all()

    workgroups = []

    active = 0
    completed = 0

    for a in assignments:

        wg = Workgroup.query.get(a.workgroup_id)

        if wg:

            workgroups.append(wg)

            if wg.is_completed == "Completed":
                completed += 1
            else:
                active += 1

    return render_template(
        "engineerDashboard.html",
        current_user=current_user,
        workgroups=workgroups,
        total=len(workgroups),
        active=active,
        completed=completed
    )

@engineer.route("/api/auth/logout", methods=["POST","GET"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))