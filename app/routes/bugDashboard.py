from flask import Blueprint, render_template, session, jsonify, request, redirect, url_for
from app.extensions import db
from app.models.bug import Bug
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment
from sqlalchemy import select

bug = Blueprint("bugDashboard", __name__)


# --------------------------------------------------
# BUG MANAGEMENT PAGE
# --------------------------------------------------
@bug.route("/bug_management")
def bug_management():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    workgroup_id = request.args.get('workgroup_id', type=int)
    workgroup = None
    
    if workgroup_id:
        workgroup = Workgroup.query.get(workgroup_id)
        if not workgroup:
            return redirect(url_for("manager.manager_dashboard"))
        
        # Authorization: Only the manager who owns this workgroup can view it
        if session.get('role') == 'Manager' and workgroup.manager_id != session['user_id']:
            return redirect(url_for("manager.manager_dashboard"))

    return render_template("bugManagement.html", workgroup=workgroup)


# --------------------------------------------------
# GET CURRENT USER
# --------------------------------------------------
@bug.route("/api/auth/me", methods=["GET"])
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

# --------------------------------------------------
# GET ALL BUGS
# --------------------------------------------------
@bug.route("/api/bugs", methods=["GET"])
def get_bugs():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    role = session.get("role")
    workgroup_id = request.args.get('workgroup_id', type=int)

    # Authorization check for workgroup access
    if workgroup_id:
        workgroup = Workgroup.query.get(workgroup_id)
        if not workgroup:
            return jsonify({"error": "Workgroup not found"}), 404
        
        # Only the manager who owns this workgroup can view its bugs
        if role == 'Manager' and workgroup.manager_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

    query = Bug.query

    if workgroup_id:
        # Filter bugs by workgroup - get engineers assigned to this workgroup
        engineer_ids = db.session.query(WorkgroupAssignment.employee_id).filter(
            WorkgroupAssignment.workgroup_id == workgroup_id
        ).all()
        engineer_ids = [e[0] for e in engineer_ids]
        
        if not engineer_ids:
            # No engineers assigned to this workgroup
            return jsonify({"repro": [], "test": []})
        
        query = query.filter(Bug.engineer_id.in_(engineer_ids))
    elif role == "Manager":
        # Only include bugs whose engineer belongs to a workgroup managed by this manager
        engineer_ids_subq = (
               db.session.query(db.func.distinct(WorkgroupAssignment.employee_id))
                .join(Workgroup, WorkgroupAssignment.workgroup_id == Workgroup.id)
                .filter(Workgroup.manager_id == user_id)
                .subquery()
        )
        

        engineer_ids = select(WorkgroupAssignment.employee_id).join(
            Workgroup,
            Workgroup.id == WorkgroupAssignment.workgroup_id
        ).where(
            Workgroup.manager_id == session["user_id"]
        )

        query = query.filter(Bug.engineer_id.in_(engineer_ids))
        
    elif role == "Engineer":
        # Engineers only see their own bugs
        query = query.filter(Bug.engineer_id == user_id)

    bugs = query.all()

    repro = []
    test = []

    for b in bugs:

        data = {
            "id": b.bug_code,
            "priority": b.priority,
            "engineer": {
                "name": b.engineer.full_name if b.engineer else "Unassigned",
                "initials": (
                    (b.engineer.first_name[0] + b.engineer.last_name[0]).upper()
                    if b.engineer else "--"
                ),
                "color": "#7c3aed"
            },
            "summary": b.summary or "",
            "tests": [t.test_name for t in b.tests],
            "stations": [s.station_name for s in b.stations],
            "config": b.station_config,
            "resourceGroup": b.resource_group
        }

        if b.bug_type == "repro":
            repro.append(data)
        else:
            test.append(data)

    return jsonify({
        "repro": repro,
        "test": test
    })

# --------------------------------------------------
# UPDATE RESOURCE GROUP
# --------------------------------------------------
@bug.route("/api/bugs/<bug_code>/resource", methods=["PATCH"])
def update_resource_group(bug_code):
    data = request.json
    bug = Bug.query.filter_by(bug_code=bug_code).first()
    bug.resource_group = data.get("resourceGroup")
    db.session.commit()
    return jsonify({"message": "Resource group updated"})

# --------------------------------------------------
# RUN BUG NOW
# --------------------------------------------------
@bug.route("/api/bugs/<bug_code>/run", methods=["POST"])
def run_bug_now(bug_code):

    bug = Bug.query.filter_by(bug_code=bug_code).first()
    bug.status = "running"
    db.session.commit()
    return jsonify({"message": "Bug execution started"})

# --------------------------------------------------
# RUN BUG LATER
# --------------------------------------------------
@bug.route("/api/bugs/<bug_code>/schedule", methods=["POST"])
def schedule_bug(bug_code):

    bug = Bug.query.filter_by(bug_code=bug_code).first()
    bug.status = "scheduled"
    db.session.commit()
    return jsonify({"message": "Bug scheduled"})

# --------------------------------------------------
# BUG STATISTICS
# --------------------------------------------------
@bug.route("/api/bugs/stats", methods=["GET"])
def bug_stats():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user_id = session["user_id"]
    role = session.get("role")
    workgroup_id = request.args.get('workgroup_id', type=int)

    # Authorization check for workgroup access
    if workgroup_id:
        workgroup = Workgroup.query.get(workgroup_id)
        if not workgroup:
            return jsonify({"error": "Workgroup not found"}), 404
        
        # Only the manager who owns this workgroup can view its stats
        if role == 'Manager' and workgroup.manager_id != user_id:
            return jsonify({"error": "Unauthorized"}), 403

    query = Bug.query

    if workgroup_id:
        # Filter bugs by workgroup
        engineer_ids = db.session.query(WorkgroupAssignment.employee_id).filter(
            WorkgroupAssignment.workgroup_id == workgroup_id
        ).all()
        engineer_ids = [e[0] for e in engineer_ids]
        
        if not engineer_ids:
            return jsonify({
                "totalBugs": 0,
                "reproBugs": 0,
                "testBugs": 0,
                "pendingActions": 0
            })
        
        query = query.filter(Bug.engineer_id.in_(engineer_ids))
    elif role == "Manager":
       engineer_ids_subq = (
            db.session.query(db.func.distinct(WorkgroupAssignment.employee_id))
            .join(Workgroup, WorkgroupAssignment.workgroup_id == Workgroup.id)
            .filter(Workgroup.manager_id == user_id)
            .subquery()
        )
       query = query.filter(Bug.engineer_id.in_(engineer_ids_subq))

    elif role == "Engineer":
        query = query.filter(Bug.engineer_id == user_id)

    total = query.count()
    repro = query.filter_by(bug_type="repro").count()
    test = query.filter_by(bug_type="test").count()
    pending = query.filter_by(status="pending").count()
    return jsonify({
        "totalBugs": total,
        "reproBugs": repro,
        "testBugs": test,
        "pendingActions": pending
    })


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
@bug.route("/api/auth/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    })