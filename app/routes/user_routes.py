from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import User, UserRole

user_bp = Blueprint("user_bp", __name__)

@user_bp.route("/")
def home():
    return "Hello"

@user_bp.route("/create", methods=["POST"])
def create_user():

    if not request.is_json:
        return {"error": "Request must be JSON"}, 400

    data = request.get_json()

    user = User(
        first_name=data.get("first_name"),
        last_name=data.get("last_name"),
        email=data.get("email"),
        role=UserRole(data.get("role")),
        password=data.get("password")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"})