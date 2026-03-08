from flask import Blueprint, jsonify, request, session, redirect, render_template, url_for
from app.extensions import db
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment

manager = Blueprint("manager", __name__)

@manager.route("/manager_dashboard")
def manager_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("managerDashboard.html")

# ---------------------------------------------------
# GET CURRENT LOGGED-IN USER
# GET /api/auth/me
# ---------------------------------------------------
@manager.route("/api/auth/me", methods=["GET"])
def get_current_user():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])

    return jsonify({
        "id": user.id,
        "name": user.first_name,
        "fullName": user.full_name,
        "email": user.email,
        "role": user.role
    })


# ---------------------------------------------------
# GET DASHBOARD STATS
# GET /api/stats
# ---------------------------------------------------
@manager.route("/api/stats", methods=["GET"])
def get_stats():

    total = Workgroup.query.count()
    active = Workgroup.query.filter_by(is_completed=False).count()
    completed = Workgroup.query.filter_by(is_completed=True).count()
    engineers = User.query.filter_by(role="Engineer").count()

    return jsonify({
        "total": total,
        "active": active,
        "completed": completed,
        "engineers": engineers
    })


# ---------------------------------------------------
# GET ALL WORKGROUPS
# GET /api/workgroups
# ---------------------------------------------------
@manager.route("/api/workgroups", methods=["GET"])
def get_workgroups():

    workgroups = Workgroup.query.all()

    data = []

    for wg in workgroups:

        assignments = WorkgroupAssignment.query.filter_by(workgroup_id=wg.id).all()
        engineers = []

        for a in assignments:
            user = User.query.get(a.employee_id)
            if user:
                engineers.append({
                    "id": user.id,
                    "name": user.full_name
                })

        data.append({
            "id": wg.id,
            "name": wg.name,
            "release_version": wg.release_version,
            "is_completed": wg.is_completed,
            "created_at": wg.created_at,
            "engineers": engineers
        })

    return jsonify(data)


# ---------------------------------------------------
# CREATE WORKGROUP
# POST /api/workgroups
# ---------------------------------------------------
@manager.route("/api/workgroups", methods=["POST"])
def create_workgroup():

    data = request.get_json()

    name = data.get("name")
    release_version = data.get("release_version")
    engineer_ids = data.get("engineer_ids", [])

    workgroup = Workgroup(
        name=name,
        release_version=release_version,
        is_completed=False
    )

    db.session.add(workgroup)
    db.session.commit()

    # assign engineers
    for eid in engineer_ids:
        assign = WorkgroupAssignment(
            workgroup_id=workgroup.id,
            engineer_id=eid
        )
        db.session.add(assign)

    db.session.commit()

    return jsonify({
        "id": workgroup.id,
        "name": workgroup.name,
        "release_version": workgroup.release_version,
        "is_completed": workgroup.is_completed,
        "created_at": workgroup.created_at,
        "engineers": []
    })


# ---------------------------------------------------
# UPDATE WORKGROUP
# PATCH /api/workgroups/<id>
# ---------------------------------------------------
@manager.route("/api/workgroups/<int:id>", methods=["PATCH"])
def update_workgroup(id):

    wg = Workgroup.query.get_or_404(id)
    data = request.get_json()

    wg.name = data.get("name", wg.name)
    wg.release_version = data.get("release_version", wg.release_version)
    wg.is_completed = data.get("is_completed", wg.is_completed)

    db.session.commit()

    return jsonify({
        "id": wg.id,
        "name": wg.name,
        "release_version": wg.release_version,
        "is_completed": wg.is_completed,
        "created_at": wg.created_at
    })


# ---------------------------------------------------
# DELETE WORKGROUP
# DELETE /api/workgroups/<id>
# ---------------------------------------------------
@manager.route("/api/workgroups/<int:id>", methods=["DELETE"])
def delete_workgroup(id):

    wg = Workgroup.query.get_or_404(id)

    WorkgroupAssignment.query.filter_by(workgroup_id=id).delete()

    db.session.delete(wg)
    db.session.commit()

    return jsonify({"message": "Workgroup deleted"})


# ---------------------------------------------------
# GET ENGINEERS
# GET /api/engineers
# ---------------------------------------------------
@manager.route("/api/engineers")
def get_engineers():

    engineers = User.query.filter_by(role="Engineer").all()

    data = []

    for e in engineers:
        data.append({
            "id": e.id,
            "name": e.full_name
        })

    return jsonify(data)

#---------------------------------------------------
# LOGOUT
#---------------------------------------------------
@manager.route("/api/auth/logout",methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "message": "Logged out successfully"
    }), 200