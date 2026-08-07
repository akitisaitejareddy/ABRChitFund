from datetime import date

from models.customer import Customer
from models.group import ChitGroup
from models.payment import Payment
from models.installment import Installment



def get_admin_dashboard_data():

    today = date.today()


    # -----------------------------
    # Total Customers
    # -----------------------------

    total_customers = Customer.query.count()



    # -----------------------------
    # Active Groups
    # -----------------------------

    active_groups = ChitGroup.query.filter_by(
        status="ACTIVE"
    ).count()



    # -----------------------------
    # Today's Collection
    # -----------------------------

    today_payments = Payment.query.filter(
        Payment.payment_date == today
    ).all()


    total_today_collection = sum(
        payment.amount
        for payment in today_payments
        if payment.amount
    )


    # Remove decimal values
    total_today_collection = round(
        total_today_collection
    )



    # -----------------------------
    # Pending Payments
    # -----------------------------

    pending_payments = Installment.query.filter_by(
        status="PENDING"
    ).count()



    # -----------------------------
    # Recent Payments
    # -----------------------------

    recent_payments = Payment.query.order_by(
        Payment.created_at.desc()
    ).limit(5).all()



    return {


        "total_customers":
            total_customers,


        "active_groups":
            active_groups,


        "today_collection":
            total_today_collection,


        "pending_payments":
            pending_payments,


        "recent_payments":
            recent_payments

    }