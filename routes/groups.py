from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required

from services.group_service import (
    get_all_groups,
    create_group
)



groups = Blueprint(
    "groups",
    __name__,
    url_prefix="/groups"
)




# ---------------------------------
# List all chit groups
# ---------------------------------

@groups.route("/")
@login_required
def list_groups():

    all_groups = get_all_groups()


    return render_template(
        "groups/list.html",
        groups=all_groups
    )




# ---------------------------------
# Create new chit group
# ---------------------------------

@groups.route("/create", methods=["GET", "POST"])
@login_required
def create():


    if request.method == "POST":


        data = {

            "name": request.form.get(
                "name"
            ),


            "description": request.form.get(
                "description"
            ),


            "group_amount": request.form.get(
                "group_amount"
            ),


            "duration_months": request.form.get(
                "duration_months"
            ),


            "start_date": request.form.get(
                "start_date"
            )

        }



        try:

            create_group(
                data
            )


            flash(
                "Chit group created successfully",
                "success"
            )


            return redirect(
                url_for(
                    "groups.list_groups"
                )
            )



        except ValueError as error:


            flash(
                str(error),
                "danger"
            )



    return render_template(
        "groups/create.html"
    )