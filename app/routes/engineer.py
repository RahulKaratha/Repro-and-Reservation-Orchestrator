from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models.user import User
from app.models.workgroup import Workgroup
from app.models.workgroupAssignment import WorkgroupAssignment

engineer = Blueprint("engineer", __name__)


@engineer.route("/engineer_dashboard", methods=["GET","POST"])
def engineer_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    engineer_id = session["user_id"]
    filter_type = request.args.get("filter", "all")

    current_user = User.query.get(engineer_id)

    assignments = WorkgroupAssignment.query.filter_by(
        employee_id=engineer_id
    ).all()

    workgroups = []
    all_workgroups = []

    active = 0
    completed = 0

    for a in assignments:

        wg = Workgroup.query.get(a.workgroup_id)

        if wg:

            # Count stats
            all_workgroups.append(wg)

            if wg.is_completed == "Completed":
                completed += 1
            else:
                active += 1

            # Fetch engineers assigned to this workgroup
            engineer_assignments = WorkgroupAssignment.query.filter_by(
                workgroup_id=wg.id
            ).all()

            engineers = []

            for ea in engineer_assignments:
                user = User.query.get(ea.employee_id)
                if user:
                    engineers.append(user)

            wg.engineer_list = engineers

            # Apply filter
            if filter_type == "active" and wg.is_completed != "Completed":
                workgroups.append(wg)

            elif filter_type == "completed" and wg.is_completed == "Completed":
                workgroups.append(wg)

            elif filter_type == "all":
                workgroups.append(wg)

    return render_template(
        "engineerDashboard.html",
        current_user=current_user,
        workgroups=workgroups,
        total=len(all_workgroups),
        active=active,
        completed=completed,
        filter_type=filter_type
    )


@engineer.route("/api/engineer/workgroups", methods=["GET"])
def get_engineer_workgroups():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    engineer_id = session["user_id"]
    filter_type = request.args.get("filter", "all")

    assignments = WorkgroupAssignment.query.filter_by(employee_id=engineer_id).all()

    workgroups = []

    for a in assignments:
        wg = Workgroup.query.get(a.workgroup_id)
        if not wg:
            continue

        # filter based on status
        if filter_type == "active" and wg.is_completed:
            continue
        if filter_type == "completed" and not wg.is_completed:
            continue

        engineer_assignments = WorkgroupAssignment.query.filter_by(workgroup_id=wg.id).all()
        engineers = []
        for ea in engineer_assignments:
            user = User.query.get(ea.employee_id)
            if user:
                engineers.append({
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                })

        workgroups.append({
            "id": wg.id,
            "name": wg.name,
            "release_version": wg.release_version,
            "is_completed": "Completed" if wg.is_completed else "Active",
            "manager": {
                "id": wg.manager.id if wg.manager else None,
                "first_name": wg.manager.first_name if wg.manager else "",
                "last_name": wg.manager.last_name if wg.manager else "",
            },
            "engineers": engineers,
        })

    return jsonify(workgroups)


@engineer.route("/api/engineer/stats", methods=["GET"])
def get_engineer_stats():

    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    engineer_id = session["user_id"]
    assignments = WorkgroupAssignment.query.filter_by(employee_id=engineer_id).all()

    total = 0
    active = 0
    completed = 0

    for a in assignments:
        wg = Workgroup.query.get(a.workgroup_id)
        if not wg:
            continue

        total += 1
        if wg.is_completed:
            completed += 1
        else:
            active += 1

    return jsonify({
        "total": total,
        "active": active,
        "completed": completed,
    })


@engineer.route("/engineer/bug_management", methods=["GET"])
def engineer_bug_management():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("engineerBugManagement.html")


@engineer.route("/engineer_logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))