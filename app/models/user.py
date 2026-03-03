from app.extensions import db
from sqlalchemy import Enum
import enum

class UserRole(enum.Enum):
    engineer = "engineer"
    manager = "manager"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    email = db.Column(db.String(50), nullable=False, unique=True)

    role = db.Column(
        Enum(UserRole),
        nullable=False
    )

    password = db.Column(db.String(255), nullable=False)