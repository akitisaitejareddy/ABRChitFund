from flask import Flask

from config import Config

from database import db

from flask_migrate import Migrate

import models


def create_app():

    app = Flask(__name__)


    # Load configuration

    app.config.from_object(Config)



    # Initialize database

    db.init_app(app)
    
    # Initialize migrations
    
    Migrate(app, db)



    @app.route("/")
    def home():

        return """

        <h1>
        ABR Chit Fund
        </h1>

        <p>
        Application Running Successfully
        </p>

        """



    return app





app = create_app()



if __name__ == "__main__":

    app.run(
        debug=True
    )