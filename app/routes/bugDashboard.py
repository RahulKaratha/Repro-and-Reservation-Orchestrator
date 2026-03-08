from flask import Blueprint, render_template, session, jsonify, request
from app.extensions import db
from app.models.bug import Bug

bug = Blueprint("bugDashboard", __name__)


# --------------------------------------------------
# BUG MANAGEMENT PAGE
# --------------------------------------------------
@bug.route("/bug_management")
def bug_management():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return render_template("bugManagement.html")


# --------------------------------------------------
# GET CURRENT USER
# --------------------------------------------------
@bug.route("/api/auth/me", methods=["GET"])
def get_current_user():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    user = session.get("user")

    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "fullName": user["name"],
        "email": user["email"],
        "role": user["role"]
    })

# --------------------------------------------------
# GET ALL BUGS
# --------------------------------------------------
@bug.route("/api/bugs", methods=["GET"])
def get_bugs():

    bugs = Bug.query.all()

    repro = []
    test = []

    for b in bugs:

        data = {
            "id": b.bug_code,
            "engineer": {
                "name": b.engineer.full_name if b.engineer else "Unassigned",
                "initials": (
                    (b.engineer.first_name[0] + b.engineer.last_name[0]).upper()
                    if b.engineer else "--"
                ),
                "color": "#7c3aed"
            },
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

    total = Bug.query.count()
    repro = Bug.query.filter_by(bug_type="repro").count()
    test = Bug.query.filter_by(bug_type="test").count()
    pending = Bug.query.filter_by(status="pending").count()
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