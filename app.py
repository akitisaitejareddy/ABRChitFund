from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config
from database import db

import models

from models.user import User

from routes.auth import auth


migrate = Migrate()

login_manager = LoginManager()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)


    # -----------------------------
    # Initialize Database
    # -----------------------------

    db.init_app(app)


    # -----------------------------
    # Initialize Migration
    # -----------------------------

    migrate.init_app(
        app,
        db
    )


    # -----------------------------
    # Initialize Login Manager
    # -----------------------------

    login_manager.init_app(
        app
    )


    login_manager.login_view = "auth.login"


    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )


    # -----------------------------
    # Register Blueprints
    # -----------------------------

    app.register_blueprint(
        auth
    )


    # -----------------------------
    # Home Route
    # -----------------------------

    @app.route("/")
    def home():

        return """
        <h1>ABR Chit Fund</h1>
        <p>Application Running Successfully</p>
        """


    return app



if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True
    )