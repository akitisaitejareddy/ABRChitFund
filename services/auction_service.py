from datetime import datetime

from database import db

from models.auction import Auction
from models.group import ChitGroup
from models.customer import Customer
from models.membership import Membership


def get_all_auctions():
    return (
        Auction.query
        .order_by(
        Auction.auction_date.desc()
    )
        .all()
    )


def get_group_members(group_id):
    return (
        Customer.query
        .join(
        Membership,
        Membership.customer_id == Customer.id
    )
        .filter(
            Membership.group_id == group_id,
            Membership.status == "ACTIVE"
        )
        .order_by(
            Customer.name
        )
        .all()
    )


def create_auction(data):

    group_id = data.get("group_id")
    winner_customer_id = data.get("winner_customer_id")
    auction_month = data.get("auction_month")
    auction_date = data.get("auction_date")
    bid_amount = data.get("bid_amount")

    if not group_id:
        raise ValueError("Group is required")

    if not winner_customer_id:
        raise ValueError("Auction winner is required")

    if not auction_month:
        raise ValueError("Auction month is required")

    if not auction_date:
        raise ValueError("Auction date is required")

    if not bid_amount:
        raise ValueError("Bid amount is required")

    try:
        group_id = int(group_id)
        winner_customer_id = int(winner_customer_id)
        auction_month = int(auction_month)
        bid_amount = float(bid_amount)

    except (ValueError, TypeError):
        raise ValueError("Invalid auction details")

    if auction_month <= 0:
        raise ValueError(
            "Auction month must be greater than zero"
        )

    if bid_amount <= 0:
        raise ValueError(
            "Bid amount must be greater than zero"
        )

    group = db.session.get(
        ChitGroup,
        group_id
    )

    if not group:
        raise ValueError("Group not found")

    if group.status != "ACTIVE":
        raise ValueError(
            "Selected group is not active"
        )

    winner = db.session.get(
        Customer,
        winner_customer_id
    )

    if not winner:
        raise ValueError("Customer not found")

    membership = (
        Membership.query
        .filter_by(
            group_id=group.id,
            customer_id=winner.id,
            status="ACTIVE"
        )
        .first()
    )

    if not membership:
        raise ValueError(
            "Selected customer is not an active member "
            "of this group"
        )

    if auction_month > group.duration_months:
        raise ValueError(
            f"Auction month cannot be greater than "
            f"{group.duration_months}"
        )

    existing_auction = (
        Auction.query
        .filter_by(
            group_id=group.id,
            auction_month=auction_month
        )
        .first()
    )

    if existing_auction:
        raise ValueError(
            f"Auction for month {auction_month} "
            f"already exists for this group"
        )

    try:
        auction_date = datetime.strptime(
            auction_date,
            "%Y-%m-%d"
        ).date()

    except (ValueError, TypeError):
        raise ValueError("Invalid auction date")

    commission_amount = (
        group.group_amount * 4
    ) / 100

    net_bid_amount = (
        bid_amount -
        commission_amount
    )

    if net_bid_amount <= 0:
        raise ValueError(
            "Bid amount must be greater than "
            "the commission amount"
        )

    monthly_installment = (
        (
            group.group_amount -
            net_bid_amount
        )
        /
        group.duration_months
    )

    auction = Auction(
        group_id=group.id,
        winner_customer_id=winner.id,
        auction_month=auction_month,
        auction_date=auction_date,
        bid_amount=bid_amount,
        commission_amount=commission_amount,
        net_bid_amount=net_bid_amount,
        installment_amount=monthly_installment,
        status="COMPLETED"
    )

    db.session.add(auction)

    db.session.commit()

    return auction

# ---------------------------------
# Delete Auction
# ---------------------------------

def delete_auction(auction_id):

    auction = db.session.get(
        Auction,
        auction_id
    )


    if not auction:

        raise ValueError(
            "Auction not found"
        )


    db.session.delete(
        auction
    )


    db.session.commit()


    return True
