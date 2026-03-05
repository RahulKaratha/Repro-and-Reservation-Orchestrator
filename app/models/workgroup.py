from app.extensions import db
from sqlalchemy import Enum
import enum
from datetime import datetime, timezone

class StatusEnum(enum.Enum):
    Completed = "Completed"
    Active = "Active"

class Workgroup(db.Model):

    __tablename__ = "workgroup_schema"

    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(100), nullable=False)
    release_version = db.Column("Release_Version", db.String(20), nullable=False)
    is_completed = db.Column("Status", db.String(10), nullable=False, default="Active")
    manager_id = db.Column("Manager_ID", db.Integer, db.ForeignKey("users.ID"))
    created_at = db.Column("Created_At", db.DateTime,default=lambda: datetime.now(timezone.utc))

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