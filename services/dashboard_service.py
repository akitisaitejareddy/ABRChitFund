from datetime import date

from models.customer import Customer
from models.group import ChitGroup
from models.payment import Payment
from models.installment import Installment
from models.membership import Membership



def get_admin_dashboard_data():

    today = date.today()


    # ---------------------------------
    # Total Collection
    # Only active records
    # ---------------------------------

    all_payments = Payment.query.all()


    total_collection = sum(
        payment.amount
        for payment in all_payments
        if payment.amount
    )


    total_collection = round(
        total_collection
    )



    # ---------------------------------
    # Total Bid Payments
    # ---------------------------------

    total_bid_payments = 0



    # ---------------------------------
    # Today's Collection
    # ---------------------------------

    today_payments = Payment.query.filter(
        Payment.payment_date == today
    ).all()


    today_collection = sum(
        payment.amount
        for payment in today_payments
        if payment.amount
    )


    today_collection = round(
        today_collection
    )



    # ---------------------------------
    # Total Pending Amount
    # Ignore deleted groups
    # ---------------------------------

    pending_installments = (

        Installment.query

        .join(
            Membership,
            Installment.membership_id == Membership.id
        )

        .join(
            ChitGroup,
            Membership.group_id == ChitGroup.id
        )

        .filter(

            Installment.status != "PAID",

            ChitGroup.is_active == True

        )

        .all()

    )


    total_pending_amount = 0



    for installment in pending_installments:


        due_month = installment.due_month


        if (

            due_month.month == today.month

            and

            due_month.year == today.year

        ):


            balance = (

                installment.due_amount

                -

                (installment.paid_amount or 0)

            )


            if balance > 0:

                total_pending_amount += balance



    total_pending_amount = round(
        total_pending_amount
    )



    # ---------------------------------
    # Recent Payments
    # ---------------------------------

    recent_payments = Payment.query.order_by(

        Payment.created_at.desc()

    ).limit(5).all()



    return {


        "total_collection":
            total_collection,


        "total_bid_payments":
            total_bid_payments,


        "today_collection":
            today_collection,


        "total_pending_amount":
            total_pending_amount,


        "recent_payments":
            recent_payments

    }