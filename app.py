from flask import Flask

from config import Config

from database import db

import models

from flask_migrate import Migrate

from flask_login import LoginManager

from routes.auth import auth

from routes.dashboard import dashboard

from routes.groups import groups

from routes.payments import payments

from routes.customers import customers


login_manager = LoginManager()





def create_app():


    app = Flask(__name__)



    # Configuration

    app.config.from_object(
        Config
    )



    # Database initialization

    db.init_app(
        app
    )



    # Migration

    Migrate(
        app,
        db
    )



    # Login Manager

    login_manager.init_app(
        app
    )


    login_manager.login_view = (
        "auth.login"
    )




    # Load logged-in user


    from models.user import User



    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )




    # Register blueprints


    app.register_blueprint(
        auth
    )


    app.register_blueprint(
        dashboard
    )


    app.register_blueprint(
        groups
    )


    app.register_blueprint(
        payments
    )

    app.register_blueprint(
        customers
    )



    @app.route("/")
    def home():

        return (
            "ABR Chit Fund Application Running Successfully"
        )




    return app






if __name__ == "__main__":


    app = create_app()


    app.run(
        debug=True
    )