from database import db

from models.base import BaseModel



class Customer(BaseModel):

    __tablename__ = "customers"



    # Full customer name
    name = db.Column(
        db.String(100),
        nullable=False
    )



    # Mobile number
    mobile = db.Column(
        db.String(15),
        nullable=False,
        unique=True
    )



    # Email address
    email = db.Column(
        db.String(120),
        unique=True
    )



    # Address
    address = db.Column(
        db.String(255)
    )



    # Aadhaar / ID reference
    # We store only reference number,
    # actual documents can be added later
    identity_number = db.Column(
        db.String(100)
    )



    # Customer status

    status = db.Column(
        db.String(20),
        default="ACTIVE",
        nullable=False
    )



    def __repr__(self):

        return self.name