from flask import Blueprint, session, jsonify, render_template, request, redirect, url_for
from app.extensions import db
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment
from app.auth_utils import manager_required, login_required
from datetime import datetime
from app.extensions import db, socketio     

manager = Blueprint("manager", __name__)


@manager.route("/manager", methods=["GET"])
@login_required
def manager_dashboard():
    #  FIX 5: Also verify the role at the page level so an engineer
    # cannot navigate directly to /manager by typing the URL.
    if session.get("role") != "Manager":
        return redirect(url_for("auth.login"))
    return render_template("managerDashboard.html")


@manager.route("/api/stats", methods=["GET"])
@manager_required          #  Engineer cannot call this anymore
def get_stats():
    manager_id = session["user_id"]

    total = Workgroup.query.filter_by(manager_id=manager_id).count()
    active = Workgroup.query.filter_by(manager_id=manager_id, status="Active").count()
    completed = Workgroup.query.filter_by(manager_id=manager_id, status="Completed").count()
    engineers = User.query.filter_by(role="Engineer").count()

    return jsonify({
        "total": total,
        "active": active,
        "completed": completed,
        "engineers": engineers
    })


@manager.route("/api/workgroups", methods=["GET"])
@manager_required
def get_workgroups():
    manager_id = session["user_id"]
    print(f"Fetching workgroups for manager_id: {manager_id}")  # Debug log
    workgroups = Workgroup.query.filter_by(manager_id=manager_id).all()
    print(f"Found {len(workgroups)} workgroups")  # Debug log

    result = []
    for wg in workgroups:
        assignments = WorkgroupAssignment.query.filter_by(workgroup_id=wg.id).all()
        engineers = []
        for a in assignments:
            eng = User.query.get(a.employee_id)
            if eng:
                engineers.append({"id": eng.id, "name": f"{eng.first_name} {eng.last_name}"})

        result.append({
            "id": wg.id,
            "name": wg.name,
            "release_version": wg.release_version,
            "is_completed": wg.is_completed,
            "created_at": wg.created_at.isoformat() if wg.created_at else None,
            "engineers": engineers
        })

    return jsonify(result)


@manager.route("/api/workgroups", methods=["POST"])
@manager_required
def create_workgroup():
    data = request.json
    print(f"Creating workgroup: {data}")  # Debug log

    try:
        wg = Workgroup(
            name=data["name"],
            release_version=data["release_version"],
            manager_id=session["user_id"],
            status="Completed" if data.get("is_completed", False) else "Active"
        )

        db.session.add(wg)
        db.session.flush()  # Get the ID before committing
        print(f"Workgroup created with ID: {wg.id}")  # Debug log

        engineer_ids = data.get("engineer_ids", [])
        print(f"Engineer IDs to assign: {engineer_ids}")  # Debug log
        
        for eid in engineer_ids:
            assignment = WorkgroupAssignment(workgroup_id=wg.id, employee_id=eid)
            db.session.add(assignment)
            print(f"Added assignment: workgroup={wg.id}, engineer={eid}")  # Debug log

        db.session.commit()
        print("Committed to database")  # Debug log
        socketio.emit("workgroup_created", {"workgroup_id": wg.id})
        
        # Verify assignments were saved
        saved_assignments = WorkgroupAssignment.query.filter_by(workgroup_id=wg.id).all()
        print(f"Verified {len(saved_assignments)} assignments saved")  # Debug log

        # Fetch engineers for response
        assignments = WorkgroupAssignment.query.filter_by(workgroup_id=wg.id).all()
        engineers = []
        for a in assignments:
            eng = User.query.get(a.employee_id)
            if eng:
                engineers.append({"id": eng.id, "name": f"{eng.first_name} {eng.last_name}"})

        return jsonify({
            "id": wg.id,
            "name": wg.name,
            "release_version": wg.release_version,
            "is_completed": wg.is_completed,
            "created_at": wg.created_at.isoformat() if wg.created_at else None,
            "engineers": engineers
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error creating workgroup: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500


@manager.route("/api/workgroups/<int:id>", methods=["PATCH"])
@manager_required          #  Engineer cannot edit workgroups
def update_workgroup(id):
    data = request.get_json()
    wg = Workgroup.query.get_or_404(id)

    if "name" in data:
        wg.name = data["name"]
    if "release_version" in data:
        wg.release_version = data["release_version"]
    if "is_completed" in data:
        wg.status = "Completed" if data["is_completed"] else "Active"

    if "engineer_ids" in data:
        new_ids = set(data["engineer_ids"])
        existing = WorkgroupAssignment.query.filter_by(workgroup_id=id).all()
        existing_ids = {a.employee_id for a in existing}

        remove_ids = existing_ids - new_ids
        add_ids = new_ids - existing_ids

        if remove_ids:
            WorkgroupAssignment.query.filter(
                WorkgroupAssignment.workgroup_id == id,
                WorkgroupAssignment.employee_id.in_(remove_ids)
            ).delete(synchronize_session=False)

        for eid in add_ids:
            db.session.add(WorkgroupAssignment(workgroup_id=id, employee_id=eid))

    db.session.commit()
    socketio.emit("workgroup_created", {"workgroup_id": wg.id})

    assignments = WorkgroupAssignment.query.filter_by(workgroup_id=id).all()
    engineers = []
    for a in assignments:
        eng = User.query.get(a.employee_id)
        engineers.append({"id": eng.id, "name": f"{eng.first_name} {eng.last_name}"})

    return jsonify({
        "id": wg.id,
        "name": wg.name,
        "release_version": wg.release_version,
        "is_completed": wg.is_completed,
        "created_at": wg.created_at,
        "engineers": engineers
    })


@manager.route("/api/workgroups/<int:id>", methods=["DELETE"])
@manager_required          #  Engineer cannot delete workgroups
def delete_workgroup(id):
    wg = Workgroup.query.get_or_404(id)
    WorkgroupAssignment.query.filter_by(workgroup_id=id).delete()
    db.session.delete(wg)
    db.session.commit()
    socketio.emit("workgroup_created", {"workgroup_id": wg.id})
    return jsonify({"message": "Workgroup deleted"})


@manager.route("/api/engineers", methods=["GET"])
@manager_required
def get_engineers():
    engineers = User.query.filter_by(role="Engineer").all()
    return jsonify([
        {"id": e.id, "name": f"{e.first_name} {e.last_name}", "email": e.email}
        for e in engineers
    ])
