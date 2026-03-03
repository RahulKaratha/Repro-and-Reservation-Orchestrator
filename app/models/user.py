from app.extensions import db
from flask_login import UserMixin
from sqlalchemy import Enum
import enum

class UserRole(enum.Enum):
    engineer = "engineer"
    manager = "manager"

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)

    role = db.Column(Enum(UserRole), nullable=False)

    password = db.Column(db.String(255), nullable=False)

    workgroups_managed = db.relationship("Workgroup", backref="manager", lazy=True)
    assignments = db.relationship("WorkgroupAssignment", backref="employee", lazy=True)


class Workgroup(db.Model):
    __tablename__ = "workgroups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    release_version = db.Column(db.String(50))
    status = db.Column(db.String(50))
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class WorkgroupAssignment(db.Model):
    __tablename__ = "workgroup_assignments"

    id = db.Column(db.Integer, primary_key=True)
    workgroup_id = db.Column(db.Integer, db.ForeignKey("workgroups.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)