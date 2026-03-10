from app.extensions import db

class WorkgroupAssignment(db.Model):

    __tablename__ = "Workgroup_Assignment_Schema"

    id = db.Column("ID", db.Integer, primary_key=True)

    workgroup_id = db.Column(
        "Workgroup_ID",
        db.Integer,
        db.ForeignKey("Workgroup_Schema.ID"),
        nullable=False
    )

    employee_id = db.Column(
        "Employee_ID",
        db.Integer,
        db.ForeignKey("Users.ID"),
        nullable=False
    )

    workgroup = db.relationship(
        "Workgroup",
        back_populates="engineers"
    )

    employee = db.relationship(
        "User",
        back_populates="assignments"
    )