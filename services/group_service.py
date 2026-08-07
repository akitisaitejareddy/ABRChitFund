from datetime import datetime

from database import db

from models.group import ChitGroup




def get_all_groups():

    return ChitGroup.query.order_by(
        ChitGroup.created_at.desc()
    ).all()




def create_group(data):


    # -----------------------------
    # Validate required fields
    # -----------------------------

    if not data.get("name"):

        raise ValueError(
            "Group name is required"
        )



    if not data.get("group_amount"):

        raise ValueError(
            "Group amount is required"
        )



    if not data.get("duration_months"):

        raise ValueError(
            "Duration months is required"
        )



    if not data.get("start_date"):

        raise ValueError(
            "Start date is required"
        )



    # -----------------------------
    # Convert values
    # -----------------------------

    group_amount = float(
        data.get("group_amount")
    )



    duration_months = int(
        data.get("duration_months")
    )



    if duration_months <= 0:

        raise ValueError(
            "Duration months must be greater than zero"
        )



    if group_amount <= 0:

        raise ValueError(
            "Group amount must be greater than zero"
        )



    # -----------------------------
    # Calculate installment
    # -----------------------------

    monthly_installment = (
        group_amount / duration_months
    )



    # -----------------------------
    # Convert start date
    # -----------------------------

    start_date = datetime.strptime(
        data.get("start_date"),
        "%Y-%m-%d"
    ).date()



    # -----------------------------
    # Create group
    # -----------------------------

    group = ChitGroup(

        name=data.get(
            "name"
        ),


        description=data.get(
            "description"
        ),


        group_amount=group_amount,


        duration_months=duration_months,


        monthly_installment=monthly_installment,


        start_date=start_date,


        status="ACTIVE"

    )



    db.session.add(
        group
    )


    db.session.commit()



    return group