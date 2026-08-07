from database import db

from models.base import BaseModel



class Installment(BaseModel):

    __tablename__ = "installments"



    # Membership reference

    membership_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "membership.id"
        ),

        nullable=False

    )



    # Installment number

    # Example:
    # Month 1
    # Month 2

    installment_number = db.Column(

        db.Integer,

        nullable=False

    )



    # Due month

    due_month = db.Column(

        db.Date,

        nullable=False

    )



    # Original installment amount

    due_amount = db.Column(

        db.Float,

        nullable=False

    )



    # Amount already paid

    paid_amount = db.Column(

        db.Float,

        default=0,

        nullable=False

    )



    # Remaining amount

    balance_amount = db.Column(

        db.Float,

        default=0,

        nullable=False

    )



    # Status

    # PENDING
    # PARTIAL
    # PAID

    status = db.Column(

        db.String(20),

        default="PENDING",

        nullable=False

    )



    # Relationships


    membership = db.relationship(

        "Membership",

        backref="installments"

    )



    payment_allocations = db.relationship(

        "PaymentAllocation",

        back_populates="installment",

        cascade="all, delete-orphan"

    )



    def update_status(self):

        """
        Update installment payment status
        """

        if self.paid_amount <= 0:

            self.status = "PENDING"


        elif self.paid_amount < self.due_amount:

            self.status = "PARTIAL"


        else:

            self.status = "PAID"



        self.balance_amount = (

            self.due_amount -

            self.paid_amount

        )



    def __repr__(self):

        return (

            f"Installment {self.installment_number}"

        )