from datetime import date

from models.payment import Payment
from models.payment_allocation import PaymentAllocation
from models.installment import Installment
from models.membership import Membership
from models.customer import Customer



def get_receipt_details(payment_id):


    payment = Payment.query.get(
        payment_id
    )


    if not payment:

        raise ValueError(
            "Payment not found"
        )



    customer = Customer.query.get(
        payment.customer_id
    )


    if not customer:

        raise ValueError(
            "Customer not found"
        )



    allocations = (
        PaymentAllocation.query
        .filter_by(
            payment_id=payment.id
        )
        .all()
    )



    allocation_details = []



    for allocation in allocations:


        installment = allocation.installment


        membership = installment.membership



        allocation_details.append({

            "group_name":
                membership.chit_group.name,


            "installment_number":
                installment.installment_number,


            "allocated_amount":
                round(
                    allocation.allocated_amount
                )

        })





    # -------------------------------------------------
    # Calculate outstanding due
    # Only installments whose due date has passed
    # are considered
    # -------------------------------------------------


    today = date.today()


    total_due = 0



    installments = (

        Installment.query
        .join(
            Membership
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



    for installment in installments:


        balance = (

            installment.due_amount

            -

            (installment.paid_amount or 0)

        )



        if balance > 0:

            total_due += balance



    remaining_due = round(
        total_due
    )



    amount_received = round(
        payment.amount
    )





    return {


        "receipt_number":

            payment.receipt_number,



        "customer_name":

            customer.name,



        "customer_id":

            customer.id,



        "payment_date":

            payment.payment_date,



        "payment_method":

            payment.payment_method,



        "amount_paid":

            amount_received,



        "current_balance":

            remaining_due,



        "allocations":

            allocation_details

    }