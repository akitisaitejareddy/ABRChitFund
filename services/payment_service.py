from datetime import datetime

from database import db

from models.payment import Payment
from models.installment import Installment
from models.membership import Membership



def get_all_payments():

    return Payment.query.order_by(
        Payment.created_at.desc()
    ).all()



def generate_receipt_number():

    last_payment = Payment.query.order_by(
        Payment.id.desc()
    ).first()


    if last_payment:
        next_number = last_payment.id + 1
    else:
        next_number = 1


    return (
        f"ABR-{datetime.now().year}-{next_number:05d}"
    )



def create_payment(data):


    if not data.get("installment_id"):

        raise ValueError(
            "Installment is required"
        )


    installment = Installment.query.get(
        data.get("installment_id")
    )


    if not installment:

        raise ValueError(
            "Installment not found"
        )



    existing_payment = Payment.query.filter_by(
        installment_id=installment.id
    ).first()


    if existing_payment:

        raise ValueError(
            "This installment is already paid"
        )



    payment = Payment(

        installment_id=installment.id,

        receipt_number=generate_receipt_number(),

        amount=installment.due_amount,

        payment_date=datetime.strptime(
            data.get("payment_date"),
            "%Y-%m-%d"
        ).date(),

        payment_method=data.get(
            "payment_method"
        ),

        transaction_reference=data.get(
            "transaction_reference"
        ),

        notes=data.get(
            "notes"
        )

    )


    db.session.add(payment)



    # Update installment status

    installment.status="PAID"


    db.session.commit()


    return payment