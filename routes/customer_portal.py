from flask import (
    Blueprint,
    render_template
)

from flask_login import login_required


customer_portal = Blueprint(
    "customer_portal",
    __name__,
    url_prefix="/customer-portal"
)


# -------------------------------------------------
# Customer Portal Landing Page
# -------------------------------------------------

@customer_portal.route("/")
@login_required
def index():

    return render_template(
        "customer_portal/index.html"
    )