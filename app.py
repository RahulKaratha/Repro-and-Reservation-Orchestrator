from flask import Flask
from config import Config
from extensions import db
from flask_migrate import Migrate

from routes.auth import auth
from routes.manager import manager
from routes.engineer import engineer

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(auth)
app.register_blueprint(manager)
app.register_blueprint(engineer)

if __name__ == "__main__":
    app.run(debug=True)