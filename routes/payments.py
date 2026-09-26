from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import login_required

from models.customer import Customer


from services.payment_service import (

    get_all_payments,

    create_payment,

    get_customer_due,

    delete_payment

)


from services.receipt_service import (

    get_receipt_details

)




payments = Blueprint(

    "payments",

    __name__,

    url_prefix="/payments"

)





# ---------------------------------
# Payment List
# ---------------------------------

@payments.route("/")
@login_required
def list_payments():


    payments_list = get_all_payments()



    return render_template(

        "payments/list.html",

        payments=payments_list

    )







# ---------------------------------
# Create Payment
# ---------------------------------

@payments.route(
    "/create",
    methods=["GET","POST"]
)
@login_required
def create():



    customers = Customer.query.filter_by(

        status="ACTIVE"

    ).order_by(

        Customer.name

    ).all()




    if request.method == "POST":



        data = {



            "customer_id":

                request.form.get(
                    "customer_id"
                ),



            "amount":

                request.form.get(
                    "amount"
                ),



            "payment_date":

                request.form.get(
                    "payment_date"
                ),



            "payment_method":

                request.form.get(
                    "payment_method"
                ),



            "transaction_reference":

                request.form.get(
                    "transaction_reference"
                ),



            "notes":

                request.form.get(
                    "notes"
                )


        }





        try:



            payment = create_payment(
                data
            )



            flash(

                "Payment recorded successfully",

                "success"

            )



            return redirect(

                url_for(

                    "payments.receipt",

                    payment_id=payment.id

                )

            )




        except ValueError as error:



            flash(

                str(error),

                "danger"

            )




    return render_template(

        "payments/create.html",

        customers=customers

    )








# ---------------------------------
# Customer Due API
# ---------------------------------

@payments.route(
    "/customer/<int:customer_id>/due"
)
@login_required
def customer_due(customer_id):


    due = get_customer_due(

        customer_id

    )



    return jsonify(due)







# ---------------------------------
# Receipt
# ---------------------------------

@payments.route(
    "/receipt/<int:payment_id>"
)
@login_required
def receipt(payment_id):


    receipt_data = get_receipt_details(

        payment_id

    )



    return render_template(

        "payments/receipt.html",

        receipt=receipt_data

    )








# ---------------------------------
# Delete Payment
# ---------------------------------

@payments.route(

    "/delete/<int:payment_id>",

    methods=["POST"]

)

@login_required

def delete(payment_id):


    try:



        delete_payment(

            payment_id

        )



        flash(

            "Payment deleted successfully. Installment balance restored.",

            "success"

        )



    except ValueError as error:



        flash(

            str(error),

            "danger"

        )



    return redirect(

        url_for(

            "payments.list_payments"

        )

    )