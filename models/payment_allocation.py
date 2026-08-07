from database import db

from models.base import BaseModel



class PaymentAllocation(BaseModel):

    __tablename__ = "payment_allocations"



    # Payment receipt reference

    payment_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "payments.id"
        ),

        nullable=False

    )



    # Installment where money was applied

    installment_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "installments.id"
        ),

        nullable=False

    )



    # Amount allocated to this installment

    allocated_amount = db.Column(

        db.Float,

        nullable=False

    )



    # -----------------------------
    # Relationships
    # -----------------------------


    payment = db.relationship(

        "Payment",

        back_populates="allocations"

    )



    installment = db.relationship(

        "Installment",

        back_populates="payment_allocations"

    )



    def __repr__(self):

        return (

            f"Payment Allocation {self.id}"

        )