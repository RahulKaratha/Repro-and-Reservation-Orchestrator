from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.User import User

auth = Blueprint('auth', __name__)

# ---------------- LOGIN ----------------
@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role

            flash("Login Successful!", "success")

            if user.role == "Engineer":
                return redirect(url_for('engineer.engineer_dashboard'))
            elif user.role == "Manager":
                return redirect(url_for('manager.manager_dashboard'))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        role = request.form['role']
        email = request.form['email']
        password_raw = request.form['password']
        confirm_password = request.form['confirm_password']

        if password_raw != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already exists!", "warning")
        else:
            hashed_password = generate_password_hash(password_raw)

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=hashed_password,
                role=role
            )

            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully!", "success")
            return redirect(url_for('auth.login'))

    return render_template("register.html")

# ---------------- FORGOT PASSWORD ----------------
@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user:
            flash("Reset instructions would be sent to this email.", "info")
            # Later we will implement real token system
        else:
            flash("If this email exists, reset instructions will be sent.", "info")

    return render_template("forgot_password.html")


# ---------------- LOGOUT ----------------
@auth.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('auth.login'))