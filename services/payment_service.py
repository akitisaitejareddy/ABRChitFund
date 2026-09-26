from datetime import datetime, date

from database import db

from models.payment import Payment
from models.payment_allocation import PaymentAllocation
from models.installment import Installment
from models.membership import Membership


# ---------------------------------------------------
# Get all payments
# ---------------------------------------------------

def get_all_payments():

    return Payment.query.order_by(
        Payment.created_at.desc()
    ).all()


# ---------------------------------------------------
# Generate receipt number
# ---------------------------------------------------

def generate_receipt_number():

    last_payment = Payment.query.order_by(
        Payment.id.desc()
    ).first()

    if last_payment:
        next_number = last_payment.id + 1
    else:
        next_number = 1

    return (
        f"ABR-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"
    )


# ---------------------------------------------------
# Customer Due Calculation
#
# Only installments whose due month has arrived
# are considered.
#
# Example:
#
# Joining date: August 5, 2026
# Today: August 7, 2026
#
# Only August installment is due.
#
# September and later are NOT due.
# ---------------------------------------------------

def get_customer_due(customer_id):

    today = date.today()

    installments = (
        Installment.query
        .join(
            Membership,
            Installment.membership_id == Membership.id
        )
        .filter(
            Membership.customer_id == customer_id,
            Installment.status != "PAID",
            Installment.due_month <= today
        )
        .order_by(
            Installment.due_month.asc(),
            Installment.installment_number.asc()
        )
        .all()
    )

    total_due = 0.0

    due_details = []

    for installment in installments:

        balance = (
            installment.due_amount -
            installment.paid_amount
        )

        if balance > 0:

            total_due += balance

            due_details.append({

                "installment_id":
                    installment.id,

                "installment_number":
                    installment.installment_number,

                "due_month":
                    installment.due_month.isoformat(),

                "due_amount":
                    round(balance, 2)

            })

    return {

        "total_due":
            round(total_due, 2),

        "installments":
            due_details

    }


# ---------------------------------------------------
# Create Payment
#
# Payment is automatically allocated against
# the oldest outstanding installments first.
# ---------------------------------------------------

def create_payment(data):

    customer_id = data.get(
        "customer_id"
    )

    if not customer_id:

        raise ValueError(
            "Customer is required"
        )

    try:

        customer_id = int(customer_id)

    except (TypeError, ValueError):

        raise ValueError(
            "Invalid customer"
        )


    # -----------------------------------------------
    # Validate amount
    # -----------------------------------------------

    try:

        amount_received = float(
            data.get("amount")
        )

    except (TypeError, ValueError):

        raise ValueError(
            "Invalid payment amount"
        )


    if amount_received <= 0:

        raise ValueError(
            "Payment amount must be greater than zero"
        )


    # -----------------------------------------------
    # Validate payment date
    # -----------------------------------------------

    payment_date_value = data.get(
        "payment_date"
    )

    if not payment_date_value:

        raise ValueError(
            "Payment date is required"
        )

    try:

        payment_date = datetime.strptime(
            payment_date_value,
            "%Y-%m-%d"
        ).date()

    except ValueError:

        raise ValueError(
            "Invalid payment date"
        )


    # -----------------------------------------------
    # Find outstanding installments
    #
    # Only installments that are currently due.
    # Oldest due installment is paid first.
    # -----------------------------------------------

    today = date.today()

    installments = (
        Installment.query
        .join(
            Membership,
            Installment.membership_id == Membership.id
        )
        .filter(
            Membership.customer_id == customer_id,
            Installment.status != "PAID",
            Installment.due_month <= today
        )
        .order_by(
            Installment.due_month.asc(),
            Installment.installment_number.asc()
        )
        .all()
    )


    if not installments:

        raise ValueError(
            "No pending dues found for this customer"
        )


    # -----------------------------------------------
    # Calculate total outstanding balance
    # -----------------------------------------------

    total_outstanding = 0.0

    for installment in installments:

        balance = (
            installment.due_amount -
            installment.paid_amount
        )

        if balance > 0:

            total_outstanding += balance


    if total_outstanding <= 0:

        raise ValueError(
            "No pending dues found for this customer"
        )


    # -----------------------------------------------
    # Do not allow payment greater than due
    # -----------------------------------------------

    if amount_received > total_outstanding:

        raise ValueError(
            f"Payment amount cannot exceed total due of "
            f"₹{total_outstanding:.2f}"
        )


    # -----------------------------------------------
    # Create payment
    # -----------------------------------------------

    payment = Payment(

        customer_id=customer_id,

        receipt_number=
            generate_receipt_number(),

        amount=amount_received,

        payment_date=payment_date,

        payment_method=
            data.get("payment_method"),

        transaction_reference=
            data.get("transaction_reference"),

        notes=
            data.get("notes")

    )


    db.session.add(payment)

    db.session.flush()


    # -----------------------------------------------
    # Allocate payment FIFO
    # -----------------------------------------------

    remaining_amount = amount_received


    for installment in installments:

        if remaining_amount <= 0:

            break


        installment_balance = (
            installment.due_amount -
            installment.paid_amount
        )


        if installment_balance <= 0:

            continue


        allocation_amount = min(
            remaining_amount,
            installment_balance
        )


        allocation = PaymentAllocation(

            payment_id=payment.id,

            installment_id=installment.id,

            allocated_amount=allocation_amount

        )


        db.session.add(
            allocation
        )


        # Update installment payment amount

        installment.paid_amount += (
            allocation_amount
        )


        # Recalculate status and balance

        installment.update_status()


        remaining_amount -= (
            allocation_amount
        )


    # -----------------------------------------------
    # Save transaction
    # -----------------------------------------------

    db.session.commit()


    return payment

# ---------------------------------------------------
# Delete Payment
# Reverse Allocation
# ---------------------------------------------------

def delete_payment(payment_id):


    payment = Payment.query.get(
        payment_id
    )


    if not payment:

        raise ValueError(
            "Payment not found"
        )



    allocations = PaymentAllocation.query.filter_by(
        payment_id=payment.id
    ).all()



    for allocation in allocations:


        installment = allocation.installment


        installment.paid_amount -= (
            allocation.allocated_amount
        )



        if installment.paid_amount < 0:

            installment.paid_amount = 0



        installment.update_status()



        db.session.delete(
            allocation
        )



    db.session.delete(
        payment
    )



    db.session.commit()



    return True