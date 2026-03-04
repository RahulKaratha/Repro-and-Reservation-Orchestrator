from flask import Flask
from app.config import Config
from app.extensions import db
from app.routes.auth import auth
from app.routes.manager import manager
from app.routes.engineer import engineer
from app.extensions import db, login_manager, migrate, mail
from app.routes.user_routes import user_bp


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    migrate.init_app(flask_app, db)
    mail.init_app(flask_app)

    app.register_blueprint(auth)
    app.register_blueprint(manager)
    app.register_blueprint(engineer)

    import app.auth

    flask_app.register_blueprint(user_bp)

    return flask_app