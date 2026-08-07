from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required

from services.payment_service import (
    get_all_payments,
    create_payment
)

from models.installment import Installment



payments = Blueprint(
    "payments",
    __name__,
    url_prefix="/payments"
)



@payments.route("/")
@login_required
def list_payments():

    payments_list = get_all_payments()

    return render_template(
        "payments/list.html",
        payments=payments_list
    )





@payments.route("/create", methods=["GET","POST"])
@login_required
def create():


    installments = Installment.query.all()



    if request.method == "POST":


        data = {


            "installment_id":
                request.form.get(
                    "installment_id"
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

            create_payment(data)


            flash(
                "Payment recorded successfully",
                "success"
            )


            return redirect(
                url_for(
                    "payments.list_payments"
                )
            )



        except ValueError as error:


            flash(
                str(error),
                "danger"
            )



    return render_template(
        "payments/create.html",
        installments=installments
    )