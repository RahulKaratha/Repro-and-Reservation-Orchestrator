from app.extensions import db
from sqlalchemy import Enum
import enum

class StatusEnum(enum.Enum):
    Completed = "Completed"
    Active = "Active"

class Workgroup(db.Model):
    __tablename__ = "workgroup_schema"

    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(10), nullable=False)
    release_version = db.Column("Release_Version", db.String(10), nullable=False)

    manager_id = db.Column(
        "Manager_ID",
        db.Integer,
        db.ForeignKey("users.ID")
    )

    manager = db.relationship(
        "User",
        back_populates="managed_workgroups"
    )

    assignments = db.relationship(
        "WorkgroupAssignment",
        back_populates="workgroup"
    )

    def __repr__(self):
        return f"<Workgroup {self.name}>"