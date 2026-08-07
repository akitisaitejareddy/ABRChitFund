from database import db

from models.base import BaseModel



class Payment(BaseModel):

    __tablename__ = "payments"



    # Customer who made payment

    customer_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "customers.id"
        ),

        nullable=False

    )



    # Unique receipt number

    # Example:
    # ABR-20260806-0001

    receipt_number = db.Column(

        db.String(50),

        nullable=False,

        unique=True

    )



    # Total amount received

    amount = db.Column(

        db.Float,

        nullable=False

    )



    # Date payment received

    payment_date = db.Column(

        db.Date,

        nullable=False

    )



    # Payment method

    # CASH
    # UPI
    # BANK
    # CHEQUE

    payment_method = db.Column(

        db.String(20),

        nullable=False

    )



    # Optional transaction reference

    transaction_reference = db.Column(

        db.String(100)

    )



    # Notes

    notes = db.Column(

        db.String(255)

    )



    # -----------------------------
    # Relationships
    # -----------------------------


    customer = db.relationship(

        "Customer",

        backref="payments"

    )



    allocations = db.relationship(

        "PaymentAllocation",

        back_populates="payment",

        cascade="all, delete-orphan"

    )



    def __repr__(self):

        return self.receipt_number