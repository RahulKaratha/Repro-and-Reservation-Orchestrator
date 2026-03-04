from app.extensions import db

class WorkgroupAssignment(db.Model):
    __tablename__ = "workgroup_assignment_schema"

    id = db.Column("ID", db.Integer, primary_key=True)

    workgroup_id = db.Column(
        "Workgroup_ID",
        db.Integer,
        db.ForeignKey("workgroup_schema.ID"),
        nullable=False
    )

    employee_id = db.Column(
        "Employee_ID",
        db.Integer,
        db.ForeignKey("users.ID"),
        nullable=False
    )

    workgroup = db.relationship(
        "Workgroup",
        back_populates="assignments"
    )

    employee = db.relationship(
        "User",
        back_populates="assignments"
    )

    def __repr__(self):
        return f"<Assignment User {self.employee_id} -> Workgroup {self.workgroup_id}>"