from flask import Blueprint, render_template
from flask_login import login_required


settings = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings"
)


@settings.route("/")
@login_required
def index():

    return render_template(
        "settings/index.html"
    )