from datetime import date, timedelta

from models.group import ChitGroup
from models.membership import Membership
from models.installment import Installment
from models.payment import Payment
from models.payment_allocation import PaymentAllocation


# ============================================================
# DATE RANGE
# ============================================================

def get_date_range(
    period,
    from_date=None,
    to_date=None
):
    """
    Calculate the reporting date range.

    Supported periods:
        today
        weekly
        monthly
        yearly
        custom
    """

    today = date.today()

    if period == "today":

        return today, today

    elif period == "weekly":

        start_date = (
            today -
            timedelta(
                days=today.weekday()
            )
        )

        return start_date, today

    elif period == "monthly":

        start_date = today.replace(
            day=1
        )

        return start_date, today

    elif period in (
        "year",
        "yearly"
    ):

        start_date = today.replace(
            month=1,
            day=1
        )

        return start_date, today

    elif period == "custom":

        if not from_date or not to_date:

            raise ValueError(
                "Please select both From Date and To Date."
            )

        if from_date > to_date:

            raise ValueError(
                "From Date cannot be after To Date."
            )

        return from_date, to_date

    return None, None


# ============================================================
# GROUP REPORT
# ============================================================

def get_group_report(
    period="monthly",
    from_date=None,
    to_date=None,
    group_ids=None
):
    """
    Generate group installment report.

    Relationship:

        Installment
            ↓
        Membership
            ↓
        ChitGroup
            ↓
        Customer
    """

    # --------------------------------------------------------
    # Convert dates
    # --------------------------------------------------------

    if isinstance(
        from_date,
        str
    ) and from_date:

        from_date = date.fromisoformat(
            from_date
        )

    if isinstance(
        to_date,
        str
    ) and to_date:

        to_date = date.fromisoformat(
            to_date
        )

    # --------------------------------------------------------
    # Get date range
    # --------------------------------------------------------

    start_date, end_date = get_date_range(
        period,
        from_date,
        to_date
    )

    # --------------------------------------------------------
    # Group IDs
    # --------------------------------------------------------

    if group_ids is None:

        group_ids = []

    group_ids = [

        int(group_id)

        for group_id in group_ids

        if str(group_id).strip()

    ]

    # --------------------------------------------------------
    # Get groups
    # --------------------------------------------------------

    group_query = ChitGroup.query

    if group_ids:

        group_query = group_query.filter(
            ChitGroup.id.in_(
                group_ids
            )
        )

    groups = group_query.order_by(
        ChitGroup.name.asc()
    ).all()

    selected_group_ids = [

        group.id

        for group in groups

    ]

    # --------------------------------------------------------
    # No groups
    # --------------------------------------------------------

    if not selected_group_ids:

        return {

            "groups": [],

            "rows": [],

            "summary": {

                "groups": 0,

                "members": 0,

                "installments": 0,

                "total_due": 0,

                "total_paid": 0,

                "total_pending": 0

            },

            "start_date": start_date,

            "end_date": end_date

        }

    # --------------------------------------------------------
    # Query installments
    # --------------------------------------------------------

    query = (

        Installment.query

        .join(
            Membership,
            Installment.membership_id
            == Membership.id
        )

        .filter(
            Membership.group_id.in_(
                selected_group_ids
            )
        )

    )

    # --------------------------------------------------------
    # Date filter
    #
    # Report is based on installment due month.
    # --------------------------------------------------------

    if start_date:

        query = query.filter(
            Installment.due_month
            >= start_date
        )

    if end_date:

        query = query.filter(
            Installment.due_month
            <= end_date
        )

    # --------------------------------------------------------
    # Get fresh rows from database
    # --------------------------------------------------------

    installments = query.order_by(

        Installment.due_month.asc(),

        Installment.installment_number.asc(),

        Installment.id.asc()

    ).all()

    # --------------------------------------------------------
    # Build report
    # --------------------------------------------------------

    rows = []

    total_due = 0.0

    total_paid = 0.0

    total_pending = 0.0

    unique_members = set()

    # --------------------------------------------------------
    # Process installments
    # --------------------------------------------------------

    for installment in installments:

        membership = installment.membership

        if not membership:

            continue

        group = membership.chit_group

        if not group:

            continue

        customer = membership.customer

        # ----------------------------------------------------
        # Customer
        # ----------------------------------------------------

        if customer:

            customer_name = customer.name

            customer_mobile = (
                customer.mobile or ""
            )

            customer_id = customer.id

        else:

            customer_name = "Unknown"

            customer_mobile = ""

            customer_id = None

        # ----------------------------------------------------
        # Amounts
        #
        # Recalculate balance instead of trusting stored
        # balance_amount.
        # ----------------------------------------------------

        due_amount = float(
            installment.due_amount or 0
        )

        paid_amount = float(
            installment.paid_amount or 0
        )

        balance_amount = max(

            due_amount -
            paid_amount,

            0

        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if paid_amount <= 0:

            status = "PENDING"

        elif paid_amount < due_amount:

            status = "PARTIAL"

        else:

            status = "PAID"

        # ----------------------------------------------------
        # Totals
        # ----------------------------------------------------

        total_due += due_amount

        total_paid += paid_amount

        total_pending += balance_amount

        unique_members.add(
            membership.id
        )

        # ----------------------------------------------------
        # Row
        # ----------------------------------------------------

        rows.append({

            "group_id":
                group.id,

            "group_name":
                group.name,

            "customer_id":
                customer_id,

            "customer_name":
                customer_name,

            "customer_mobile":
                customer_mobile,

            "ticket_number":
                membership.ticket_number,

            "installment_number":
                installment.installment_number,

            "due_month":
                installment.due_month,

            "due_amount":
                due_amount,

            "paid_amount":
                paid_amount,

            "balance_amount":
                balance_amount,

            "status":
                status

        })

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {

        "groups":
            len(groups),

        "members":
            len(unique_members),

        "installments":
            len(rows),

        "total_due":
            round(
                total_due,
                2
            ),

        "total_paid":
            round(
                total_paid,
                2
            ),

        "total_pending":
            round(
                total_pending,
                2
            )

    }

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "groups":
            groups,

        "rows":
            rows,

        "summary":
            summary,

        "start_date":
            start_date,

        "end_date":
            end_date

    }


# ============================================================
# PAYMENT REPORT
# ============================================================

def get_payment_report(
    period="monthly",
    from_date=None,
    to_date=None,
    group_ids=None,
    customer_id=None,
    payment_method=None
):
    """
    Generate payment collection report.

    Report is based on payment_date.

    Supports:

        today
        weekly
        monthly
        yearly
        custom

    Optional filters:

        group_ids
        customer_id
        payment_method

    Payment relationship:

        Customer
            ↓
        Payment
            ↓
        PaymentAllocation
            ↓
        Installment
            ↓
        Membership
            ↓
        ChitGroup
    """

    # --------------------------------------------------------
    # Convert dates
    # --------------------------------------------------------

    if isinstance(
        from_date,
        str
    ) and from_date:

        from_date = date.fromisoformat(
            from_date
        )

    if isinstance(
        to_date,
        str
    ) and to_date:

        to_date = date.fromisoformat(
            to_date
        )

    # --------------------------------------------------------
    # Get date range
    # --------------------------------------------------------

    start_date, end_date = get_date_range(
        period,
        from_date,
        to_date
    )

    # --------------------------------------------------------
    # Group IDs
    # --------------------------------------------------------

    if group_ids is None:

        group_ids = []

    group_ids = [

        int(group_id)

        for group_id in group_ids

        if str(group_id).strip()

    ]

    # --------------------------------------------------------
    # Customer ID
    # --------------------------------------------------------

    if customer_id:

        try:

            customer_id = int(
                customer_id
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                "Invalid customer."
            )

    else:

        customer_id = None

    # --------------------------------------------------------
    # Payment method
    # --------------------------------------------------------

    if payment_method:

        payment_method = (
            payment_method
            .strip()
            .upper()
        )

    else:

        payment_method = None

    # --------------------------------------------------------
    # Payment query
    # --------------------------------------------------------

    query = Payment.query

    # --------------------------------------------------------
    # Payment date filter
    # --------------------------------------------------------

    if start_date:

        query = query.filter(
            Payment.payment_date >= start_date
        )

    if end_date:

        query = query.filter(
            Payment.payment_date <= end_date
        )

    # --------------------------------------------------------
    # Customer filter
    # --------------------------------------------------------

    if customer_id:

        query = query.filter(
            Payment.customer_id == customer_id
        )

    # --------------------------------------------------------
    # Payment method filter
    # --------------------------------------------------------

    if payment_method:

        query = query.filter(
            Payment.payment_method == payment_method
        )

    # --------------------------------------------------------
    # Get payments
    # --------------------------------------------------------

    payments = query.order_by(

        Payment.payment_date.desc(),

        Payment.id.desc()

    ).all()

    # --------------------------------------------------------
    # Build rows
    # --------------------------------------------------------

    rows = []

    total_received = 0.0

    payment_count = 0

    unique_customers = set()

    unique_groups = set()

    # --------------------------------------------------------
    # Process payments
    # --------------------------------------------------------

    for payment in payments:

        customer = payment.customer

        if not customer:

            continue

        # ----------------------------------------------------
        # Get allocations
        # ----------------------------------------------------

        allocations = (
            PaymentAllocation.query
            .filter_by(
                payment_id=payment.id
            )
            .all()
        )

        # ----------------------------------------------------
        # Determine groups involved
        # ----------------------------------------------------

        allocation_groups = []

        for allocation in allocations:

            installment = (
                allocation.installment
            )

            if not installment:

                continue

            membership = (
                installment.membership
            )

            if not membership:

                continue

            group = (
                membership.chit_group
            )

            if not group:

                continue

            # -----------------------------------------------
            # Group filter
            # -----------------------------------------------

            if group_ids:

                if group.id not in group_ids:

                    continue

            allocation_groups.append({

                "group_id":
                    group.id,

                "group_name":
                    group.name,

                "membership_id":
                    membership.id,

                "ticket_number":
                    membership.ticket_number,

                "installment_number":
                    installment.installment_number,

                "allocated_amount":
                    float(
                        allocation.allocated_amount
                        or 0
                    )

            })

        # ----------------------------------------------------
        # Group filter
        # ----------------------------------------------------

        if group_ids and not allocation_groups:

            continue

        # ----------------------------------------------------
        # Report amount
        #
        # No group filter:
        #     Entire payment amount.
        #
        # Group filter:
        #     Only allocation amount belonging to selected
        #     groups.
        # ----------------------------------------------------

        if group_ids:

            report_amount = sum(

                item["allocated_amount"]

                for item in allocation_groups

            )

        else:

            report_amount = float(
                payment.amount or 0
            )

        # ----------------------------------------------------
        # Skip zero-value records
        # ----------------------------------------------------

        if report_amount <= 0:

            continue

        # ----------------------------------------------------
        # Group names
        # ----------------------------------------------------

        group_names = sorted(

            set(

                item["group_name"]

                for item in allocation_groups

            )

        )

        # ----------------------------------------------------
        # Tracking
        # ----------------------------------------------------

        unique_customers.add(
            customer.id
        )

        for item in allocation_groups:

            unique_groups.add(
                item["group_id"]
            )

        # ----------------------------------------------------
        # Totals
        # ----------------------------------------------------

        total_received += report_amount

        payment_count += 1

        # ----------------------------------------------------
        # Row
        # ----------------------------------------------------

        rows.append({

            "payment_id":
                payment.id,

            "receipt_number":
                payment.receipt_number,

            "payment_date":
                payment.payment_date,

            "customer_id":
                customer.id,

            "customer_name":
                customer.name,

            "customer_mobile":
                customer.mobile or "",

            "group_names":
                group_names,

            "group_text":
                ", ".join(group_names)
                if group_names
                else "Unallocated",

            "amount":
                report_amount,

            "payment_method":
                payment.payment_method,

            "transaction_reference":
                payment.transaction_reference
                or "",

            "notes":
                payment.notes
                or "",

            "allocations":
                allocation_groups

        })

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {

        "payments":
            payment_count,

        "customers":
            len(unique_customers),

        "groups":
            len(unique_groups),

        "total_received":
            round(
                total_received,
                2
            )

    }

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "rows":
            rows,

        "summary":
            summary,

        "start_date":
            start_date,

        "end_date":
            end_date

    }
    
    # ============================================================
# AUCTION REPORT
# ============================================================

def get_auction_report(
    period="monthly",
    from_date=None,
    to_date=None,
    group_ids=None
):
    """
    Generate auction report.

    Report is based on auction_date.

    Supports:
        today
        weekly
        monthly
        yearly
        custom

    Optional filters:
        group_ids
    """

    # --------------------------------------------------------
    # Imports
    # --------------------------------------------------------

    from models.auction import Auction
    from models.group import ChitGroup
    from models.customer import Customer

    # --------------------------------------------------------
    # Convert dates
    # --------------------------------------------------------

    if isinstance(from_date, str) and from_date:
        from_date = date.fromisoformat(from_date)

    if isinstance(to_date, str) and to_date:
        to_date = date.fromisoformat(to_date)

    # --------------------------------------------------------
    # Get date range
    # --------------------------------------------------------

    start_date, end_date = get_date_range(
        period,
        from_date,
        to_date
    )

    # --------------------------------------------------------
    # Group IDs
    # --------------------------------------------------------

    if group_ids is None:
        group_ids = []

    group_ids = [
        int(group_id)
        for group_id in group_ids
        if str(group_id).strip()
    ]

    # --------------------------------------------------------
    # Auction query
    # --------------------------------------------------------

    query = (
        Auction.query
        .join(
            ChitGroup,
            Auction.group_id == ChitGroup.id
        )
        .join(
            Customer,
            Auction.winner_customer_id == Customer.id
        )
    )

    # --------------------------------------------------------
    # Date filter
    # --------------------------------------------------------

    if start_date:
        query = query.filter(
            Auction.auction_date >= start_date
        )

    if end_date:
        query = query.filter(
            Auction.auction_date <= end_date
        )

    # --------------------------------------------------------
    # Group filter
    # --------------------------------------------------------

    if group_ids:
        query = query.filter(
            Auction.group_id.in_(group_ids)
        )

    # --------------------------------------------------------
    # Get auctions
    # --------------------------------------------------------

    auctions = (
        query
        .order_by(
            Auction.auction_date.desc(),
            Auction.auction_month.desc(),
            Auction.id.desc()
        )
        .all()
    )

    # --------------------------------------------------------
    # Build rows
    # --------------------------------------------------------

    rows = []

    total_bid_amount = 0.0
    total_commission = 0.0
    total_net_bid = 0.0
    total_installment = 0.0

    unique_groups = set()
    unique_winners = set()

    # --------------------------------------------------------
    # Process auctions
    # --------------------------------------------------------

    for auction in auctions:

        group = auction.group
        winner = auction.winner

        if not group:
            continue

        if not winner:
            continue

        # ----------------------------------------------------
        # Amounts
        # ----------------------------------------------------

        bid_amount = float(
            auction.bid_amount or 0
        )

        commission_amount = float(
            auction.commission_amount or 0
        )

        net_bid_amount = float(
            auction.net_bid_amount or 0
        )

        installment_amount = float(
            auction.installment_amount or 0
        )

        # ----------------------------------------------------
        # Tracking
        # ----------------------------------------------------

        unique_groups.add(
            group.id
        )

        unique_winners.add(
            winner.id
        )

        # ----------------------------------------------------
        # Totals
        # ----------------------------------------------------

        total_bid_amount += bid_amount
        total_commission += commission_amount
        total_net_bid += net_bid_amount
        total_installment += installment_amount

        # ----------------------------------------------------
        # Row
        # ----------------------------------------------------

        rows.append({

            "auction_id":
                auction.id,

            "auction_date":
                auction.auction_date,

            "auction_month":
                auction.auction_month,

            "group_id":
                group.id,

            "group_name":
                group.name,

            "winner_customer_id":
                winner.id,

            "winner_name":
                winner.name,

            "winner_mobile":
                winner.mobile or "",

            "bid_amount":
                bid_amount,

            "commission_amount":
                commission_amount,

            "net_bid_amount":
                net_bid_amount,

            "installment_amount":
                installment_amount,

            "status":
                auction.status

        })

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {

        "auctions":
            len(rows),

        "groups":
            len(unique_groups),

        "winners":
            len(unique_winners),

        "total_bid_amount":
            round(
                total_bid_amount,
                2
            ),

        "total_commission":
            round(
                total_commission,
                2
            ),

        "total_net_bid":
            round(
                total_net_bid,
                2
            ),

        "total_installment":
            round(
                total_installment,
                2
            )
    }

    # --------------------------------------------------------
    # Return report
    # --------------------------------------------------------

    return {

        "start_date":
            start_date,

        "end_date":
            end_date,

        "rows":
            rows,

        "summary":
            summary
    }