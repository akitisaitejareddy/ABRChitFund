from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required

from database import db

from models.customer import Customer
from models.group import ChitGroup

from services.customer_service import (
    get_all_customers,
    get_customer,
    create_customer,
    update_customer,
    add_customer_to_group,
    delete_customer
)



customers = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
)



# -------------------------------------------------
# List Customers
# -------------------------------------------------

@customers.route("/")
@login_required
def list_customers():

    all_customers = get_all_customers()

    return render_template(
        "customers/list.html",
        customers=all_customers
    )



# -------------------------------------------------
# Create Customer
# Multiple Groups Supported
# -------------------------------------------------

@customers.route(
    "/create",
    methods=["GET", "POST"]
)
@login_required
def create():


    groups = ChitGroup.query.filter_by(
        status="ACTIVE"
    ).order_by(
        ChitGroup.name
    ).all()



    if request.method == "POST":


        data = {

            "name": request.form.get("name"),

            "mobile": request.form.get("mobile"),

            "email": request.form.get("email"),

            "address": request.form.get("address"),

            "identity_number": request.form.get(
                "identity_number"
            ),

            "group_ids": request.form.getlist(
                "group_ids"
            ),

            "joining_date": request.form.get(
                "joining_date"
            )

        }



        try:


            create_customer(data)


            flash(
                "Customer created successfully.",
                "success"
            )


            return redirect(

                url_for(
                    "customers.list_customers"
                )

            )



        except ValueError as error:


            flash(
                str(error),
                "danger"
            )



    return render_template(
        "customers/create.html",
        groups=groups
    )





# -------------------------------------------------
# Edit Customer
# -------------------------------------------------

@customers.route(
    "/<int:customer_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit(customer_id):


    customer = get_customer(
        customer_id
    )



    if not customer:


        flash(
            "Customer not found.",
            "danger"
        )


        return redirect(

            url_for(
                "customers.list_customers"
            )

        )




    if request.method == "POST":



        data = {


            "name": request.form.get(
                "name"
            ),


            "mobile": request.form.get(
                "mobile"
            ),


            "email": request.form.get(
                "email"
            ),


            "address": request.form.get(
                "address"
            ),


            "identity_number": request.form.get(
                "identity_number"
            ),


            "status": request.form.get(
                "status"
            )

        }




        try:


            update_customer(

                customer_id,

                data

            )



            flash(

                "Customer updated successfully.",

                "success"

            )



            return redirect(

                url_for(
                    "customers.list_customers"
                )

            )




        except ValueError as error:


            flash(

                str(error),

                "danger"

            )




    return render_template(

        "customers/edit.html",

        customer=customer

    )





# -------------------------------------------------
# Add Existing Customer To New Group
# -------------------------------------------------

@customers.route(
    "/<int:customer_id>/add-group",
    methods=["GET", "POST"]
)
@login_required
def add_group(customer_id):


    customer = get_customer(
        customer_id
    )



    if not customer:


        flash(
            "Customer not found.",
            "danger"
        )


        return redirect(

            url_for(
                "customers.list_customers"
            )

        )



    groups = ChitGroup.query.filter_by(

        status="ACTIVE"

    ).order_by(

        ChitGroup.name

    ).all()




    if request.method == "POST":


        try:


            add_customer_to_group(

                customer_id,

                request.form.get(
                    "group_id"
                ),

                request.form.get(
                    "joining_date"
                )

            )



            flash(

                "Customer added to group successfully.",

                "success"

            )



            return redirect(

                url_for(
                    "customers.list_customers"
                )

            )



        except ValueError as error:


            flash(

                str(error),

                "danger"

            )




    return render_template(

        "customers/add_group.html",

        customer=customer,

        groups=groups

    )





# -------------------------------------------------
# Delete Customer
# -------------------------------------------------

@customers.route(
    "/<int:customer_id>/delete"
)
@login_required
def delete(customer_id):


    try:


        delete_customer(

            customer_id

        )


        flash(

            "Customer deleted successfully.",

            "success"

        )


    except ValueError as error:


        flash(

            str(error),

            "danger"

        )



    return redirect(

        url_for(
            "customers.list_customers"
        )

    )