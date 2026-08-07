from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)


from flask_login import (
    login_required,
    current_user
)


from services.dashboard_service import (
    get_admin_dashboard_data
)



dashboard = Blueprint(
    "dashboard",
    __name__
)





@dashboard.route("/dashboard")
@login_required
def dashboard_home():


    if not current_user.role:


        flash(
            "No role assigned to your account.",
            "danger"
        )


        return redirect(
            url_for("auth.logout")
        )




    dashboard_data = get_admin_dashboard_data()





    return render_template(

        "dashboard/dashboard.html",

        user=current_user,

        **dashboard_data

    )