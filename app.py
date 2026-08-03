from flask import Flask

from config import Config

from database import db

from flask_migrate import Migrate

import models

from routes.auth import auth



def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)


    # Initialize Database

    db.init_app(app)


    # Initialize Migration

    Migrate(app, db)


    # Register Routes

    app.register_blueprint(auth)


    @app.route("/")
    def home():

        return "Dashboard Coming Soon"


    return app



if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True
    )