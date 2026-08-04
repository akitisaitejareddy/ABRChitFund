from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)

from services.auth_service import authenticate_user


auth = Blueprint(
    "auth",
    __name__
)



@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("home")
        )


    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )


        user = authenticate_user(
            username,
            password
        )


        if not user:

            flash(
                "Invalid username or password",
                "danger"
            )

            return redirect(
                url_for("auth.login")
            )


        login_user(
            user
        )


        flash(
            "Login successful",
            "success"
        )


        return redirect(
            url_for("home")
        )


    return render_template(
        "login.html"
    )



@auth.route(
    "/logout"
)
@login_required
def logout():

    logout_user()


    flash(
        "You have been logged out.",
        "success"
    )


    return redirect(
        url_for("auth.login")
    )