from app.extensions import db
from sqlalchemy import Enum
import enum

class RoleEnum(enum.Enum):
    Engineer = "Engineer"
    Manager = "Manager"


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