from flask import Blueprint, session, jsonify, render_template
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment
from flask import request
from datetime import datetime
from app import db

manager = Blueprint("manager", __name__)

@manager.route("/manager",methods=["GET"])
def manager_dashboard():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return render_template("managerDashboard.html")

@manager.route("/api/auth/me", methods=["GET"])
def get_current_user():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.get(session["user_id"])

    return jsonify({
        "id": user.id,
        "name": user.first_name,
        "fullName": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "role": user.role
    })


@manager.route("/api/stats", methods=["GET"])
def get_stats():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    manager_id = session["user_id"]

    total = Workgroup.query.filter_by(manager_id=manager_id).count()

    active = Workgroup.query.filter_by(
    manager_id=manager_id,
    status="Active"
    ).count()

    completed = Workgroup.query.filter_by(
        manager_id=manager_id,
        status="Completed"
    ).count()

    engineers = User.query.filter_by(role="Engineer").count()

    return jsonify({
        "total": total,
        "active": active,
        "completed": completed,
        "engineers": engineers
    })


@manager.route("/api/workgroups", methods=["GET"])
def get_workgroups():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    manager_id = session["user_id"]

    workgroups = Workgroup.query.filter_by(manager_id=manager_id).all()

    result = []

    for wg in workgroups:

        assignments = WorkgroupAssignment.query.filter_by(
            workgroup_id=wg.id
        ).all()

        engineers = []

        for a in assignments:
            eng = User.query.get(a.employee_id)

            engineers.append({
                "id": eng.id,
                "name": f"{eng.first_name} {eng.last_name}"
            })

        result.append({
            "id": wg.id,
            "name": wg.name,
            "release_version": wg.release_version,
            "is_completed": wg.is_completed,
            "created_at": wg.created_at,
            "engineers": engineers
        })

    return jsonify(result)

@manager.route("/api/workgroups", methods=["POST"])
def create_workgroup():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json

    wg = Workgroup(
        name=data["name"],
        release_version=data["release_version"],
        manager_id=session["user_id"],
        status="Completed" if data.get("is_completed", False) else "Active",
        created_at=datetime.utcnow()
    )

    db.session.add(wg)
    db.session.commit()

    engineer_ids = data.get("engineer_ids", [])

    for eid in engineer_ids:
        assignment = WorkgroupAssignment(
            workgroup_id=wg.id,
            employee_id=eid
        )
        db.session.add(assignment)

    db.session.commit()

    return jsonify({
        "id": wg.id,
        "name": wg.name,
        "release_version": wg.release_version,
        "is_completed": wg.is_completed,
        "created_at": wg.created_at,
        "engineers": []
    })


@manager.route("/api/workgroups/<int:id>", methods=["PATCH"])
def update_workgroup(id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    wg = Workgroup.query.get_or_404(id)

    # Update basic fields
    if "name" in data:
        wg.name = data["name"]

    if "release_version" in data:
        wg.release_version = data["release_version"]

    if "is_completed" in data:
        wg.status = "Completed" if data["is_completed"] else "Active"

    # 🔹 Update engineers if provided
    if "engineer_ids" in data:

        new_employee_ids = set(data["engineer_ids"])

        # Get existing assignments
        existing_assignments = WorkgroupAssignment.query.filter_by(
            workgroup_id=id
        ).all()

        existing_employee_ids = {a.employee_id for a in existing_assignments}

        # Engineers to remove
        remove_ids = existing_employee_ids - new_employee_ids

        # Engineers to add
        add_ids = new_employee_ids - existing_employee_ids

        # Remove old assignments
        if remove_ids:
            WorkgroupAssignment.query.filter(
                WorkgroupAssignment.workgroup_id == id,
                WorkgroupAssignment.employee_id.in_(remove_ids)
            ).delete(synchronize_session=False)

        # Add new assignments
        for employee_id in add_ids:
            assignment = WorkgroupAssignment(
                workgroup_id=id,
                employee_id=employee_id
            )
            db.session.add(assignment)

    db.session.commit()

    # 🔹 Return updated workgroup with engineers
    assignments = WorkgroupAssignment.query.filter_by(workgroup_id=id).all()

    engineers = []
    for a in assignments:
        eng = User.query.get(a.employee_id)
        engineers.append({
            "id": eng.id,
            "name": f"{eng.first_name} {eng.last_name}"
        })

    return jsonify({
        "id": wg.id,
        "name": wg.name,
        "release_version": wg.release_version,
        "is_completed": wg.is_completed,
        "created_at": wg.created_at,
        "engineers": engineers
    })


@manager.route("/api/workgroups/<int:id>", methods=["DELETE"])
def delete_workgroup(id):

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    wg = Workgroup.query.get_or_404(id)

    WorkgroupAssignment.query.filter_by(workgroup_id=id).delete()

    db.session.delete(wg)
    db.session.commit()

    return jsonify({"message": "Workgroup deleted"})


@manager.route("/api/engineers", methods=["GET"])
def get_engineers():

    engineers = User.query.filter_by(role="Engineer").all()

    result = []

    for e in engineers:
        result.append({
            "id": e.id,
            "name": f"{e.first_name} {e.last_name}",
            "email": e.email
        })

    return jsonify(result)


@manager.route("/api/auth/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({"message": "Logged out"})