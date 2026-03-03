from extensions import db
from sqlalchemy import Enum
import enum


# ---------------- ENUMS ----------------

class RoleEnum(enum.Enum):
    Engineer = "Engineer"
    Manager = "Manager"


class StatusEnum(enum.Enum):
    Completed = "Completed"
    Active = "Active"


# ---------------- USERS TABLE ----------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column("ID", db.Integer, primary_key=True)
    first_name = db.Column("First_Name", db.String(10), nullable=False)
    last_name = db.Column("Last_Name", db.String(10))
    email = db.Column("Email", db.String(100), unique=True, nullable=False)
    password = db.Column("Password", db.String(255), nullable=False)
    role = db.Column("Role", Enum(RoleEnum), nullable=False)

    # Relationships
    managed_workgroups = db.relationship(
        "Workgroup",
        backref="manager",
        cascade="all, delete",
        foreign_keys="Workgroup.manager_id"
    )

    assigned_workgroups = db.relationship(
        "WorkgroupAssignment",
        back_populates="employee",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.email}>"


# ---------------- WORKGROUP TABLE ----------------

class Workgroup(db.Model):
    __tablename__ = "workgroup_schema"

    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(10), nullable=False)
    release_version = db.Column("Release_Version", db.String(10), nullable=False)
    status = db.Column("Status", Enum(StatusEnum), default=StatusEnum.Active, nullable=False)

    manager_id = db.Column(
        "Manager_ID",
        db.Integer,
        db.ForeignKey("users.ID", ondelete="CASCADE", onupdate="CASCADE")
    )

    # Relationship to assignments
    assignments = db.relationship(
        "WorkgroupAssignment",
        back_populates="workgroup",
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Workgroup {self.name}>"


# ---------------- WORKGROUP ASSIGNMENT TABLE ----------------

class WorkgroupAssignment(db.Model):
    __tablename__ = "workgroup_assignment_schema"

    id = db.Column("ID", db.Integer, primary_key=True)

    workgroup_id = db.Column(
        "Workgroup_ID",
        db.Integer,
        db.ForeignKey("workgroup_schema.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    employee_id = db.Column(
        "Employee_ID",
        db.Integer,
        db.ForeignKey("users.ID", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False
    )

    # Relationships
    workgroup = db.relationship("Workgroup", back_populates="assignments")
    employee = db.relationship("User", back_populates="assigned_workgroups")

    def __repr__(self):
        return f"<Assignment User {self.employee_id} -> Workgroup {self.workgroup_id}>"