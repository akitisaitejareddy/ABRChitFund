from datetime import datetime

from database import db

from models.group import ChitGroup

from models.membership import Membership




def get_all_groups():
    
    return ChitGroup.query.filter_by(
        is_active=True
    ).order_by(
        ChitGroup.created_at.desc()
    ).all()





def create_group(data):


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



    group_amount = float(
        data.get("group_amount")
    )



    duration_months = int(
        data.get("duration_months")
    )



    if group_amount <= 0:

        raise ValueError(
            "Group amount must be greater than zero"
        )



    if duration_months <= 0:

        raise ValueError(
            "Duration must be greater than zero"
        )



    monthly_installment = (
        group_amount / duration_months
    )



    start_date = datetime.strptime(
        data.get("start_date"),
        "%Y-%m-%d"
    ).date()



    group = ChitGroup(

        name=data.get("name"),

        description=data.get("description"),

        group_amount=group_amount,

        duration_months=duration_months,

        monthly_installment=monthly_installment,

        start_date=start_date,

        status="ACTIVE"

    )



    db.session.add(group)

    db.session.commit()



    return group





# ---------------------------------
# Update Group Name Only
# ---------------------------------

def update_group_name(group_id, name):


    group = ChitGroup.query.get(
        group_id
    )



    if not group:

        raise ValueError(
            "Group not found"
        )



    if not name:

        raise ValueError(
            "Group name is required"
        )



    group.name = name



    db.session.commit()



    return group





# ---------------------------------
# Delete Group
# ---------------------------------

# ---------------------------------
# Delete Group
# ---------------------------------

def delete_group(group_id):

    group = db.session.get(
        ChitGroup,
        group_id
    )


    if not group:

        raise ValueError(
            "Group not found"
        )


    # Check only active memberships
    active_memberships = Membership.query.filter_by(
        group_id=group.id,
        status="ACTIVE"
    ).count()


    if active_memberships > 0:

        raise ValueError(
            "Cannot delete group. Active customers are enrolled."
        )


    # Soft delete group
    group.status = "INACTIVE"
    group.is_active = False


    db.session.commit()


    return True