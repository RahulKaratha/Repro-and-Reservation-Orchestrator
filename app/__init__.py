from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate, mail
from app.routes.user_routes import user_bp


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    migrate.init_app(flask_app, db)
    mail.init_app(flask_app)

    login_manager.login_view = "user_bp.login_page"

    import app.auth

    flask_app.register_blueprint(user_bp)

    return flask_app