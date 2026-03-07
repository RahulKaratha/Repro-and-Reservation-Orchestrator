from flask import Blueprint, render_template, session, redirect, url_for, request
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

            # Attach engineers to workgroup
            wg.engineers = engineers

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


@engineer.route("/engineer_logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))