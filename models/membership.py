from database import db

from models.base import BaseModel



class Membership(BaseModel):

    __tablename__ = "membership"



    # Customer reference

    customer_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "customers.id"
        ),

        nullable=False

    )



    # Chit Group reference

    group_id = db.Column(

        db.Integer,

        db.ForeignKey(
            "chit_groups.id"
        ),

        nullable=False

    )



    # Customer ticket number
    # Example:
    # Group has 30 members
    # Customer gets ticket 12

    ticket_number = db.Column(

        db.Integer,

        nullable=False

    )



    # Date customer joined the group

    joining_date = db.Column(

        db.Date,

        nullable=False

    )



    # Membership status

    status = db.Column(

        db.String(20),

        default="ACTIVE",

        nullable=False

    )



    # Relationships


    customer = db.relationship(

        "Customer",

        backref="memberships"

    )



    chit_group = db.relationship(

        "ChitGroup",

        backref="memberships"

    )





    def __repr__(self):

        return (
            f"{self.customer_id}-{self.group_id}"
        )