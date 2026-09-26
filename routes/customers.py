from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required

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

from services.audit_service import log_action


customers = Blueprint(
    "customers",
    __name__,
    url_prefix="/customers"
)


# ============================================================
# Helper
# ============================================================

def customer_audit_values(customer):
    """
    Return safe customer information for audit logging.
    """

    if not customer:
        return None

    return {
        "id": customer.id,
        "name": customer.name,
        "mobile": customer.mobile,
        "email": customer.email,
        "address": customer.address,
        "identity_number": customer.identity_number,
        "status": customer.status
    }


# ============================================================
# List Customers
# ============================================================

@customers.route("/")
@login_required
def list_customers():

    all_customers = get_all_customers()

    return render_template(
        "customers/list.html",
        customers=all_customers
    )


# ============================================================
# Create Customer
# Multiple Groups Supported
# ============================================================

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

            "group_ids": request.form.getlist(
                "group_ids"
            ),

            "joining_date": request.form.get(
                "joining_date"
            )

        }

        try:

            create_customer(data)

            # ------------------------------------------------
            # Find newly created customer
            # ------------------------------------------------

            customer = Customer.query.filter_by(
                mobile=data["mobile"]
            ).first()

            # ------------------------------------------------
            # Audit CREATE
            # ------------------------------------------------

            if customer:

                log_action(

                    action="CREATE",

                    entity_type="CUSTOMER",

                    entity_id=customer.id,

                    description=(
                        f"Customer created: "
                        f"{customer.name}"
                    ),

                    new_values=
                        customer_audit_values(
                            customer
                        )

                )

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


# ============================================================
# Edit Customer
# ============================================================

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

        # ----------------------------------------------------
        # Capture old values BEFORE update
        # ----------------------------------------------------

        old_values = customer_audit_values(
            customer
        )

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

            # ------------------------------------------------
            # Get updated customer
            # ------------------------------------------------

            updated_customer = get_customer(
                customer_id
            )

            # ------------------------------------------------
            # Audit UPDATE
            # ------------------------------------------------

            if updated_customer:

                log_action(

                    action="UPDATE",

                    entity_type="CUSTOMER",

                    entity_id=customer_id,

                    description=(
                        f"Customer updated: "
                        f"{updated_customer.name}"
                    ),

                    old_values=old_values,

                    new_values=
                        customer_audit_values(
                            updated_customer
                        )

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


# ============================================================
# Add Existing Customer To New Group
# ============================================================

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

        group_id = request.form.get(
            "group_id"
        )

        joining_date = request.form.get(
            "joining_date"
        )

        try:

            add_customer_to_group(
                customer_id,
                group_id,
                joining_date
            )

            # ------------------------------------------------
            # Find selected group
            # ------------------------------------------------

            group = ChitGroup.query.get(
                int(group_id)
            )

            group_name = (
                group.name
                if group
                else f"Group ID {group_id}"
            )

            # ------------------------------------------------
            # Audit GROUP ENROLLMENT
            # ------------------------------------------------

            log_action(

                action="CREATE",

                entity_type="MEMBERSHIP",

                entity_id=customer_id,

                description=(
                    f"Customer "
                    f"{customer.name} "
                    f"added to group "
                    f"{group_name}"
                ),

                new_values={

                    "customer_id":
                        customer_id,

                    "customer_name":
                        customer.name,

                    "group_id":
                        int(group_id)
                        if group_id
                        else None,

                    "group_name":
                        group_name,

                    "joining_date":
                        joining_date

                }

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


# ============================================================
# Delete Customer
# ============================================================

@customers.route(
    "/<int:customer_id>/delete"
)
@login_required
def delete(customer_id):

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

    # --------------------------------------------------------
    # Capture information BEFORE deletion
    # --------------------------------------------------------

    old_values = customer_audit_values(
        customer
    )

    customer_name = customer.name

    try:

        delete_customer(
            customer_id
        )

        # ----------------------------------------------------
        # Audit DELETE
        # ----------------------------------------------------

        log_action(

            action="DELETE",

            entity_type="CUSTOMER",

            entity_id=customer_id,

            description=(
                f"Customer deleted: "
                f"{customer_name}"
            ),

            old_values=old_values

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
