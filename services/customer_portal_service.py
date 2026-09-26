from datetime import date

from models.customer import Customer
from models.membership import Membership
from models.installment import Installment
from models.payment import Payment
from models.payment_allocation import PaymentAllocation



# ---------------------------------------------------
# Get Customer Complete Portal Details
# ---------------------------------------------------

def get_customer_portal_details(customer_id):


    customer = Customer.query.get(
        customer_id
    )


    if not customer:

        raise ValueError(
            "Customer not found"
        )



    today = date.today()



    # ------------------------------------------------
    # Customer Groups
    # ------------------------------------------------

    memberships = (
        Membership.query
        .filter_by(
            customer_id=customer.id
        )
        .all()
    )



    groups = []


    for membership in memberships:


        groups.append({

            "group_name":
                membership.chit_group.name,


            "ticket_number":
                membership.ticket_number,


            "joining_date":
                membership.joining_date,


            "status":
                membership.status

        })



    # ------------------------------------------------
    # Installment History
    #
    # Only from joining month
    # until current month
    #
    # Future installments ignored
    # ------------------------------------------------


    installments = (

        Installment.query

        .join(
            Membership,
            Installment.membership_id ==
            Membership.id
        )

        .filter(

            Membership.customer_id ==
            customer.id,


            Installment.due_month <= today

        )

        .order_by(

            Installment.due_month.asc()

        )

        .all()

    )



    installment_history = []


    total_outstanding = 0



    for installment in installments:


        balance = (

            installment.due_amount

            -

            installment.paid_amount

        )



        if balance < 0:

            balance = 0



        total_outstanding += balance



        installment_history.append({

            "month":

                installment.due_month.strftime(
                    "%b-%Y"
                ),


            "installment_number":

                installment.installment_number,


            "due_amount":

                round(
                    installment.due_amount
                ),


            "paid_amount":

                round(
                    installment.paid_amount
                ),


            "balance":

                round(
                    balance
                ),


            "status":

                installment.status

        })



    # ------------------------------------------------
    # Payment History
    # ------------------------------------------------


    payments = (

        Payment.query

        .filter_by(

            customer_id=customer.id

        )

        .order_by(

            Payment.payment_date.desc()

        )

        .all()

    )



    payment_history = []



    for payment in payments:


        payment_history.append({

            "receipt_number":

                payment.receipt_number,


            "date":

                payment.payment_date,


            "amount":

                round(
                    payment.amount
                ),


            "payment_method":

                payment.payment_method,


            "notes":

                payment.notes

        })



    # ------------------------------------------------
    # Return Portal Data
    # ------------------------------------------------


    return {


        "customer": {

            "id":
                customer.id,


            "name":
                customer.name,


            "mobile":
                customer.mobile,


            "email":
                customer.email,


            "address":
                customer.address

        },



        "groups":

            groups,



        "installments":

            installment_history,



        "payments":

            payment_history,



        "outstanding_due":

            round(
                total_outstanding
            )

    }