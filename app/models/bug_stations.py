from app.extensions import db


class BugStation(db.Model):

    __tablename__ = "Bug_stations"

    id = db.Column(db.Integer, primary_key=True)

    bug_id = db.Column(
        db.Integer,
        db.ForeignKey("Bugs.id")
    )

    station_name = db.Column(db.String(100))

    bug = db.relationship(
        "Bug",
        back_populates="stations"
    )