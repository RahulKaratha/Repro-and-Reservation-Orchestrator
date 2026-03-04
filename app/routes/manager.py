from flask import Blueprint, jsonify, render_template, session, request, redirect, url_for
from app.extensions import db
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment

manager = Blueprint("manager", __name__)


# DASHBOARD PAGE
@manager.route("/manager_dashboard")
def manager_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("managerDashboard.html")


# CURRENT USER
@manager.route("/api/auth/me")
def current_user():
    user = User.query.get(session["user_id"])

    return jsonify({
        "id": user.id,
        "name": user.first_name,
        "fullName": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "role": user.role
    })


# LOGOUT
@manager.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# STATS
@manager.route("/api/stats")
def stats():

    manager_id = session["user_id"]

    workgroups = Workgroup.query.filter_by(manager_id=manager_id).all()

    total = len(workgroups)
    active = len([w for w in workgroups if not w.is_completed])
    completed = len([w for w in workgroups if w.is_completed])
    engineers = User.query.filter_by(role="Engineer").count()

    return jsonify({
        "total": total,
        "active": active,
        "completed": completed,
        "engineers": engineers
    })


# ENGINEERS
@manager.route("/api/engineers")
def engineers():

    users = User.query.filter_by(role="Engineer").all()

    result = []

    for u in users:
        result.append({
            "id": u.id,
            "name": f"{u.first_name} {u.last_name}",
            "email": u.email
        })

    return jsonify(result)


# GET WORKGROUPS
@manager.route("/api/workgroups")
def workgroups():

    manager_id = session["user_id"]

    wgs = Workgroup.query.filter_by(manager_id=manager_id).all()

    result = []

    for wg in wgs:

        assignments = WorkgroupAssignment.query.filter_by(
            workgroup_id=wg.id
        ).all()

        engineers = []

        for a in assignments:
            user = User.query.get(a.employee_id)

            engineers.append({
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "email": user.email
            })

        result.append({
            "id": wg.id,
            "name": wg.workgroup_name,
            "release_version": wg.release_version,
            "is_completed": wg.is_completed,
            "created_at": wg.created_at,
            "engineers": engineers
        })

    return jsonify(result)


# CREATE WORKGROUP
@manager.route("/api/workgroups", methods=["POST"])
def create_workgroup():

    data = request.json

    wg = Workgroup(
        workgroup_name=data["name"],
        release_version=data["release_version"],
        manager_id=session["user_id"],
        is_completed=data.get("is_completed", False)
    )

    db.session.add(wg)
    db.session.commit()

    for eid in data.get("engineer_ids", []):
        assignment = WorkgroupAssignment(
            workgroup_id=wg.id,
            employee_id=eid
        )
        db.session.add(assignment)

    db.session.commit()

    return jsonify({
        "id": wg.id,
        "name": wg.workgroup_name,
        "release_version": wg.release_version,
        "is_completed": wg.is_completed,
        "created_at": wg.created_at,
        "engineers": []
    })


# UPDATE WORKGROUP
@manager.route("/api/workgroups/<int:id>", methods=["PATCH"])
def update_workgroup(id):

    wg = Workgroup.query.get_or_404(id)

    data = request.json

    wg.workgroup_name = data.get("name", wg.workgroup_name)
    wg.release_version = data.get("release_version", wg.release_version)
    wg.is_completed = data.get("is_completed", wg.is_completed)

    db.session.commit()

    return jsonify({"success": True})


# DELETE WORKGROUP
@manager.route("/api/workgroups/<int:id>", methods=["DELETE"])
def delete_workgroup(id):

    WorkgroupAssignment.query.filter_by(workgroup_id=id).delete()

    wg = Workgroup.query.get_or_404(id)

    db.session.delete(wg)

    db.session.commit()

    return jsonify({"success": True})