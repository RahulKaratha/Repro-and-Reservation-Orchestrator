from app.extensions import db

class User(db.Model):

    __tablename__ = "Users"

    id = db.Column("ID", db.Integer, primary_key=True)
    first_name = db.Column("First_Name", db.String(10), nullable=False)
    last_name = db.Column("Last_Name", db.String(10))
    email = db.Column("Email", db.String(100), unique=True, nullable=False)
    password = db.Column("Password", db.String(255), nullable=False)
    role = db.Column("Role", db.Enum('Engineer', 'Manager'), nullable=False)

    # Relationships
    managed_workgroups = db.relationship(
        "Workgroup",
        back_populates="manager",
        lazy=True
    )

    assignments = db.relationship(
        "WorkgroupAssignment",
        back_populates="employee",
        lazy=True
    )

    bugs = db.relationship(
        "Bug",
        back_populates="engineer",
        lazy=True
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()