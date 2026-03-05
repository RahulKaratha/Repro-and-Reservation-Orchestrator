from flask import Blueprint, jsonify, session, render_template, redirect, url_for
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment
from app.models.user import User

engineer = Blueprint("engineer", __name__)


@engineer.route("/engineer_dashboard")
def engineer_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("engineerDashboard.html")



@engineer.route("/api/engineer/stats")
def engineer_stats():

    engineer_id = session["user_id"]

    assignments = WorkgroupAssignment.query.filter_by(
        employee_id=engineer_id
    ).all()

    workgroups = [Workgroup.query.get(a.workgroup_id) for a in assignments]

    assigned = len(workgroups)
    active = len([w for w in workgroups if not w.is_completed])
    completed = len([w for w in workgroups if w.is_completed])

    return jsonify({
        "assigned": assigned,
        "active": active,
        "completed": completed
    })



@engineer.route("/api/engineer/workgroups")
def engineer_workgroups():

    engineer_id = session["user_id"]

    assignments = WorkgroupAssignment.query.filter_by(
        employee_id=engineer_id
    ).all()

    result = []

    for a in assignments:

        wg = Workgroup.query.get(a.workgroup_id)

        result.append({
            "id": wg.id,
            "name": wg.workgroup_name,
            "release_version": wg.release_version,
            "is_completed": wg.is_completed,
            "created_at": wg.created_at
        })

    return jsonify(result)