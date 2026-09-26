import os

from flask import Flask, redirect, url_for

from config import Config

from database import db

import models

# IMPORTANT:
# Load automatic audit event listeners.
import services.audit_events

from flask_migrate import Migrate

from flask_login import LoginManager

from routes.auth import auth
from routes.dashboard import dashboard
from routes.groups import groups
from routes.payments import payments
from routes.customers import customers
from routes.customer_portal import customer_portal
from routes.auctions import auctions
from routes.reports import reports
from routes.settings import settings


# ============================================================
# LOGIN MANAGER
# ============================================================

login_manager = LoginManager()


# ============================================================
# CREATE APPLICATION
# ============================================================

def create_app():

    instance_path = "/tmp" if os.environ.get("VERCEL") else None
    app = Flask(__name__, instance_path=instance_path)
    if os.environ.get("VERCEL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:////tmp/abrchitfund.db")
        __name__
    )

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    app.config.from_object(
        Config
    )

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    db.init_app(
        app
    )

    # --------------------------------------------------------
    # Migration
    # --------------------------------------------------------

    Migrate(
        app,
        db
    )

    # --------------------------------------------------------
    # Login Manager
    # --------------------------------------------------------

    login_manager.init_app(
        app
    )

    login_manager.login_view = (
        "auth.login"
    )

    # --------------------------------------------------------
    # Load logged-in user
    # --------------------------------------------------------

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )

    # --------------------------------------------------------
    # Register Blueprints
    # --------------------------------------------------------

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

    app.register_blueprint(
        customer_portal
    )

    app.register_blueprint(
        auctions
    )

    app.register_blueprint(
        reports
    )

    app.register_blueprint(
        settings
    )

    # --------------------------------------------------------
    # Home
    # --------------------------------------------------------

    @app.route("/")
    def home():
        return redirect(url_for("auth.login"))

    with app.app_context():
        try:
            db.create_all()
            from services.create_admin import create_admin_user
            create_admin_user()
        except Exception:
            pass
    return app


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app = create_app()

    app.run(
        debug=True
    )
app = create_app()