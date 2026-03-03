from flask import Flask
from app.config import Config
from app.extensions import db
from app.routes.auth import auth
from app.routes.manager import manager
from app.routes.engineer import engineer

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(manager)
    app.register_blueprint(engineer)

    return app