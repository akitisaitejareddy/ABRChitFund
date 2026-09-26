from database import db

from models.base import BaseModel


class Auction(BaseModel):

    __tablename__ = "auctions"

    group_id = db.Column(
        db.Integer,
        db.ForeignKey("chit_groups.id"),
        nullable=False
    )

    winner_customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    auction_month = db.Column(
        db.Integer,
        nullable=False
    )

    auction_date = db.Column(
        db.Date,
        nullable=False
    )

    bid_amount = db.Column(
        db.Float,
        nullable=False
    )

    commission_amount = db.Column(
        db.Float,
        nullable=False
    )

    net_bid_amount = db.Column(
        db.Float,
        nullable=False
    )

    installment_amount = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="COMPLETED"
    )

    group = db.relationship(
        "ChitGroup",
        backref="auctions"
    )

    winner = db.relationship(
        "Customer"
    )

    def __repr__(self):
        return f"Auction Month {self.auction_month}"