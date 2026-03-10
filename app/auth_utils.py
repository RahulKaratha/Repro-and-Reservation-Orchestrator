from app.extensions import login_manager, mail
from app.models.user import User
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import current_app, url_for, session, jsonify
from functools import wraps


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#  FIX 4: Role-enforcement decorators.
# Every sensitive route MUST use these instead of only checking "user_id in session".
# This closes the hole where an engineer could POST to /api/workgroups (manager-only).

def login_required(f):
    """Blocks any unauthenticated request."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        return f(*args, **kwargs)
    return decorated


def manager_required(f):
    """Blocks anyone who is not a Manager — even if they are logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        if session.get("role") != "Manager":
            return jsonify({"error": "Access denied: Manager role required"}), 403
        return f(*args, **kwargs)
    return decorated


def engineer_required(f):
    """Blocks anyone who is not an Engineer — even if they are logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        if session.get("role") != "Engineer":
            return jsonify({"error": "Access denied: Engineer role required"}), 403
        return f(*args, **kwargs)
    return decorated


# ── Password reset helpers ────────────────────────────────────────────────────

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SERIALIZER_SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, max_age=1800):
    serializer = URLSafeTimedSerializer(current_app.config['SERIALIZER_SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None
    return email


def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)

    msg = Message(
        subject='RRO Platform — Password Reset Request',
        recipients=[user.email],
        html=(
            f'<p>Hi {user.first_name},</p>'
            f'<p>Click the link below to reset your password. '
            f'This link expires in 30 minutes.</p>'
            f'<p><a href="{reset_url}">{reset_url}</a></p>'
            f'<p>If you did not request this, ignore this email.</p>'
        )
    )
    mail.send(msg)
