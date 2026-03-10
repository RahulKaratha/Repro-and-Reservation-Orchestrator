from app.extensions import db


class Bug(db.Model):

    __tablename__ = "Bugs"

    id = db.Column(db.Integer, primary_key=True)

    bug_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    bug_type = db.Column(
        db.Enum('repro', 'test'),
        nullable=False
    )

    engineer_id = db.Column(
        db.Integer,
        db.ForeignKey("Users.ID")
    )

    station_config = db.Column(db.String(100))
    resource_group = db.Column(db.String(100))

    status = db.Column(
        db.Enum('pending', 'running', 'scheduled', 'completed'),
        default='pending'
    )

    created_at = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp()
    )

    engineer = db.relationship(
        "User",
        back_populates="bugs"
    )

    tests = db.relationship(
        "BugTest",
        back_populates="bug",
        cascade="all, delete"
    )

    stations = db.relationship(
        "BugStation",
        back_populates="bug",
        cascade="all, delete"
    )