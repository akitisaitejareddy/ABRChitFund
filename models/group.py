from database import db

from models.base import BaseModel



class ChitGroup(BaseModel):

    __tablename__ = "chit_groups"



    # Chit Group Name
    # Example: ABR Premium 10L
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )



    # Optional group description
    description = db.Column(
        db.String(255)
    )



    # Total value of the chit group
    # Example: 1000000 = 10 Lakhs
    group_amount = db.Column(
        db.Float,
        nullable=False
    )



    # Number of months
    # In chit fund:
    # Duration Months = Number of Subscribers
    duration_months = db.Column(
        db.Integer,
        nullable=False
    )



    # Automatically calculated:
    # Group Amount / Duration Months
    monthly_installment = db.Column(
        db.Float,
        nullable=False
    )



    # Mandatory group start date
    # Used for:
    # - Payment schedule
    # - Auction dates
    # - Reports
    start_date = db.Column(
        db.Date,
        nullable=False
    )



    # Group status:
    # ACTIVE
    # COMPLETED
    # CLOSED
    status = db.Column(
        db.String(20),
        default="ACTIVE",
        nullable=False
    )



    def __repr__(self):

        return self.name