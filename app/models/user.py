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
    role = db.Column("Role", db.String(20), nullable=False)

    # Manager relationship
    managed_workgroups = db.relationship(
        "Workgroup",
        back_populates="manager"
    )

    # Engineer assignments
    assignments = db.relationship(
        "WorkgroupAssignment",
        back_populates="employee"
    )

    def __repr__(self):
        return f"<User {self.email}>"