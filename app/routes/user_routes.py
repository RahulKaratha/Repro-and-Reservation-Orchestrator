from flask import Blueprint, request, jsonify,render_template, redirect, url_for, flash
from app.extensions import db
from app.models.user import User, UserRole
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/")
def login_page():
    return render_template("login.html")

@user_bp.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@user_bp.route("/create", methods=["POST"])
def create_user():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    role = request.form.get("role")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for("user_bp.register"))

    if len(password) < 6:
        flash("Password must be at least 6 characters")
        return redirect(url_for("user_bp.register"))

    if User.query.filter_by(email=email).first():
        flash("Email already registered")
        return redirect(url_for("user_bp.register"))

    hashed_password = generate_password_hash(password)

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=UserRole(role),
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    flash("Account created successfully! Please sign in.","")
    return redirect(url_for("user_bp.login"))

@user_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for("user_bp.dashboard"))

    flash("Invalid email or password")
    return redirect(url_for("user_bp.login"))



@user_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@user_bp.route("/logout")
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for("user_bp.login"))