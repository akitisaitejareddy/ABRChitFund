from flask import Blueprint, render_template, request, redirect, url_for, flash

from models.user import User
from utils.password import check_password


auth = Blueprint(
    "auth",
    __name__
)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")


        user = User.query.filter_by(
            username=username
        ).first()


        if not user:

            flash(
                "Invalid username or password"
            )

            return redirect(
                url_for("auth.login")
            )


        if not check_password(
            password,
            user.password_hash
        ):

            flash(
                "Invalid username or password"
            )

            return redirect(
                url_for("auth.login")
            )


        if user.approval_status != "APPROVED":

            flash(
                "Your account is waiting for admin approval"
            )

            return redirect(
                url_for("auth.login")
            )


        return redirect(
            url_for("home")
        )


    return render_template(
        "login.html"
    )