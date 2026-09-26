from datetime import date, timedelta

from models.payment import Payment
from models.payment_allocation import PaymentAllocation


# ============================================================
# DATE RANGE
# ============================================================

def get_payment_date_range(
    period,
    from_date=None,
    to_date=None
):
    today = date.today()

    if period == "today":
        return today, today

    elif period == "weekly":
        start_date = today - timedelta(
            days=today.weekday()
        )
        return start_date, today

    elif period == "monthly":
        start_date = today.replace(day=1)
        return start_date, today

    elif period == "yearly":
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

        if isinstance(from_date, str):
            from_date = date.fromisoformat(
                from_date
            )

        if isinstance(to_date, str):
            to_date = date.fromisoformat(
                to_date
            )

        if from_date > to_date:
            raise ValueError(
                "From Date cannot be after To Date."
            )

        return from_date, to_date

    return None, None


# ============================================================
# PAYMENT REPORT
# ============================================================

def get_payment_report(
    period="monthly",
    from_date=None,
    to_date=None,
    customer_ids=None,
    payment_methods=None
):

    # --------------------------------------------------------
    # Convert dates
    # --------------------------------------------------------

    if isinstance(from_date, str) and from_date:
        from_date = date.fromisoformat(
            from_date
        )

    if isinstance(to_date, str) and to_date:
        to_date = date.fromisoformat(
            to_date
        )

    # --------------------------------------------------------
    # Date range
    # --------------------------------------------------------

    start_date, end_date = get_payment_date_range(
        period,
        from_date,
        to_date
    )

    # --------------------------------------------------------
    # Payment query
    # --------------------------------------------------------

    query = Payment.query

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

    if customer_ids:
        query = query.filter(
            Payment.customer_id.in_(
                customer_ids
            )
        )

    # --------------------------------------------------------
    # Payment method filter
    # --------------------------------------------------------

    if payment_methods:
        query = query.filter(
            Payment.payment_method.in_(
                payment_methods
            )
        )

    payments = query.order_by(
        Payment.payment_date.desc(),
        Payment.id.desc()
    ).all()

    # --------------------------------------------------------
    # Build rows
    # --------------------------------------------------------

    rows = []

    total_payment_amount = 0
    total_allocated_amount = 0

    unique_customers = set()
    unique_payments = set()

    method_totals = {
        "CASH": 0,
        "UPI": 0,
        "BANK": 0,
        "CHEQUE": 0
    }

    # --------------------------------------------------------
    # Process payments
    # --------------------------------------------------------

    for payment in payments:

        customer = payment.customer

        customer_name = (
            customer.name
            if customer
            else "Unknown"
        )

        customer_mobile = (
            customer.mobile
            if customer
            else ""
        )

        payment_amount = (
            payment.amount or 0
        )

        # Payment totals are counted ONCE
        total_payment_amount += payment_amount

        unique_payments.add(
            payment.id
        )

        if customer:
            unique_customers.add(
                customer.id
            )

        method = (
            payment.payment_method
            or ""
        ).upper()

        if method in method_totals:
            method_totals[method] += payment_amount

        # ----------------------------------------------------
        # Allocations
        # ----------------------------------------------------

        allocations = (
            PaymentAllocation.query
            .filter_by(
                payment_id=payment.id
            )
            .all()
        )

        # ----------------------------------------------------
        # Payment with NO allocation
        # ----------------------------------------------------

        if not allocations:

            rows.append({

                "payment_id":
                    payment.id,

                "receipt_number":
                    payment.receipt_number,

                "payment_date":
                    payment.payment_date,

                "customer_id":
                    customer.id
                    if customer
                    else None,

                "customer_name":
                    customer_name,

                "customer_mobile":
                    customer_mobile,

                "group_name":
                    "Not Allocated",

                "ticket_number":
                    "",

                "installment_number":
                    "",

                "due_month":
                    None,

                "payment_amount":
                    payment_amount,

                "allocated_amount":
                    0,

                "payment_method":
                    payment.payment_method,

                "transaction_reference":
                    payment.transaction_reference
                    or "",

                "notes":
                    payment.notes
                    or ""

            })

            continue

        # ----------------------------------------------------
        # Payment with allocations
        # ----------------------------------------------------

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

            allocated_amount = (
                allocation.allocated_amount
                or 0
            )

            total_allocated_amount += (
                allocated_amount
            )

            rows.append({

                "payment_id":
                    payment.id,

                "receipt_number":
                    payment.receipt_number,

                "payment_date":
                    payment.payment_date,

                "customer_id":
                    customer.id
                    if customer
                    else None,

                "customer_name":
                    customer_name,

                "customer_mobile":
                    customer_mobile,

                "group_name":
                    group.name
                    if group
                    else "Unknown",

                "ticket_number":
                    membership.ticket_number,

                "installment_number":
                    installment.installment_number,

                "due_month":
                    installment.due_month,

                "payment_amount":
                    payment_amount,

                "allocated_amount":
                    allocated_amount,

                "payment_method":
                    payment.payment_method,

                "transaction_reference":
                    payment.transaction_reference
                    or "",

                "notes":
                    payment.notes
                    or ""

            })

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = {

        "payments":
            len(unique_payments),

        "customers":
            len(unique_customers),

        "total_amount":
            round(
                total_payment_amount,
                2
            ),

        "total_allocated":
            round(
                total_allocated_amount,
                2
            ),

        "unallocated":
            round(
                total_payment_amount
                - total_allocated_amount,
                2
            ),

        "cash":
            round(
                method_totals["CASH"],
                2
            ),

        "upi":
            round(
                method_totals["UPI"],
                2
            ),

        "bank":
            round(
                method_totals["BANK"],
                2
            ),

        "cheque":
            round(
                method_totals["CHEQUE"],
                2
            )
    }

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