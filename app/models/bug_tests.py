from app.extensions import db


class BugTest(db.Model):

    __tablename__ = "Bug_Tests"

    id = db.Column(db.Integer, primary_key=True)

    bug_id = db.Column(
        db.Integer,
        db.ForeignKey("Bugs.id")
    )

    test_name = db.Column(db.String(100))

    bug = db.relationship(
        "Bug",
        back_populates="tests"
    )