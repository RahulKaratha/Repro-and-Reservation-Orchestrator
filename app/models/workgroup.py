from app.extensions import db

class Workgroup(db.Model):

    __tablename__ = "Workgroup_Schema"

    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(100))
    release_version = db.Column("Release_Version", db.String(10), nullable=False)

    status = db.Column(
        "Status",
        db.Enum('Completed', 'Active'),
        nullable=False,
        default="Active",
        server_default="Active"
    )

    manager_id = db.Column(
        "Manager_ID",
        db.Integer,
        db.ForeignKey("Users.ID")
    )

    created_at = db.Column(
        "Created_At",
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    manager = db.relationship(
        "User",
        back_populates="managed_workgroups"
    )

    engineers = db.relationship(
        "WorkgroupAssignment",
        back_populates="workgroup",
        cascade="all, delete"
    )

    @property
    def is_completed(self):
        return self.status == "Completed"