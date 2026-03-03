# app/__init__.py
from flask import Flask
from .config import Config
from .extensions import db, login_manager, mail, migrate
import os

def create_app():
    # set template_folder to one level up
    template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    app = Flask(__name__, template_folder=template_folder)
    app.config.from_object(Config)
    print("Flask root path:", app.root_path)
    print("Template folder:", app.template_folder)
    db.init_app(app)
    # login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from . import models
    from .routes import main
    app.register_blueprint(main)

    return app