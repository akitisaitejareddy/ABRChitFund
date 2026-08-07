from datetime import datetime
from dateutil.relativedelta import relativedelta

from database import db

from models.customer import Customer
from models.group import ChitGroup
from models.membership import Membership
from models.installment import Installment



# -------------------------------------------------
# Get All Customers
# -------------------------------------------------

def get_all_customers():

    return Customer.query.order_by(
        Customer.created_at.desc()
    ).all()



# -------------------------------------------------
# Get Customer By ID
# -------------------------------------------------

def get_customer(customer_id):

    return db.session.get(
        Customer,
        customer_id
    )



# -------------------------------------------------
# Create Customer + Multiple Group Memberships
# -------------------------------------------------

def create_customer(data):


    name = (
        data.get("name") or ""
    ).strip()


    mobile = (
        data.get("mobile") or ""
    ).strip()


    email = (
        data.get("email") or ""
    ).strip()


    address = (
        data.get("address") or ""
    ).strip()


    identity_number = (
        data.get("identity_number") or ""
    ).strip()



    group_ids = data.get(
        "group_ids",
        []
    )


    joining_date = data.get(
        "joining_date"
    )



    if not name:

        raise ValueError(
            "Customer name is required."
        )


    if not mobile:

        raise ValueError(
            "Mobile number is required."
        )


    if not group_ids:

        raise ValueError(
            "Please select at least one chit group."
        )


    if not joining_date:

        raise ValueError(
            "Joining date is required."
        )



    if Customer.query.filter_by(
        mobile=mobile
    ).first():

        raise ValueError(
            "Mobile number already exists."
        )



    if email:

        if Customer.query.filter_by(
            email=email
        ).first():

            raise ValueError(
                "Email already exists."
            )



    joining_date = datetime.strptime(
        joining_date,
        "%Y-%m-%d"
    ).date()



    try:


        customer = Customer(

            name=name,

            mobile=mobile,

            email=email or None,

            address=address or None,

            identity_number=identity_number or None,

            status="ACTIVE"

        )


        db.session.add(customer)

        db.session.flush()



        for group_id in group_ids:


            add_customer_to_group(

                customer.id,

                int(group_id),

                joining_date.strftime("%Y-%m-%d")

            )



        db.session.commit()


        return customer



    except Exception:


        db.session.rollback()

        raise





# -------------------------------------------------
# Update Customer Details
# -------------------------------------------------

def update_customer(customer_id, data):


    customer = db.session.get(
        Customer,
        customer_id
    )


    if not customer:

        raise ValueError(
            "Customer not found."
        )



    name = (
        data.get("name") or ""
    ).strip()


    mobile = (
        data.get("mobile") or ""
    ).strip()



    if not name:

        raise ValueError(
            "Customer name is required."
        )


    if not mobile:

        raise ValueError(
            "Mobile number is required."
        )



    duplicate_mobile = Customer.query.filter(

        Customer.mobile == mobile,

        Customer.id != customer_id

    ).first()



    if duplicate_mobile:

        raise ValueError(
            "Mobile number already exists."
        )



    email = (
        data.get("email") or ""
    ).strip()



    if email:


        duplicate_email = Customer.query.filter(

            Customer.email == email,

            Customer.id != customer_id

        ).first()



        if duplicate_email:

            raise ValueError(
                "Email already exists."
            )



    customer.name = name

    customer.mobile = mobile

    customer.email = email or None

    customer.address = (
        data.get("address") or None
    )


    customer.identity_number = (

        data.get("identity_number")
        or None

    )


    customer.status = data.get(
        "status",
        "ACTIVE"
    )



    db.session.commit()



    return customer





# -------------------------------------------------
# Add Existing Customer To New Group
# -------------------------------------------------

def add_customer_to_group(
    customer_id,
    group_id,
    joining_date
):


    customer = db.session.get(
        Customer,
        customer_id
    )


    if not customer:

        raise ValueError(
            "Customer not found."
        )



    group = db.session.get(
        ChitGroup,
        group_id
    )


    if not group:

        raise ValueError(
            "Group not found."
        )



    existing = Membership.query.filter_by(

        customer_id=customer.id,

        group_id=group.id

    ).first()



    if existing:

        raise ValueError(
            "Customer already belongs to this group."
        )



    active_members = Membership.query.filter_by(

        group_id=group.id,

        status="ACTIVE"

    ).count()



    if active_members >= group.duration_months:

        raise ValueError(
            "Selected group is already full."
        )



    joining_date = datetime.strptime(

        joining_date,

        "%Y-%m-%d"

    ).date()



    membership = Membership(

        customer_id=customer.id,

        group_id=group.id,

        ticket_number=active_members + 1,

        joining_date=joining_date,

        status="ACTIVE"

    )



    db.session.add(
        membership
    )


    db.session.flush()



    for month in range(

        1,

        group.duration_months + 1

    ):


        due_date = (

            group.start_date +

            relativedelta(

                months=month - 1

            )

        )



        installment = Installment(

            membership_id=membership.id,

            installment_number=month,

            due_month=due_date,

            due_amount=group.monthly_installment,

            status="PENDING"

        )


        db.session.add(
            installment
        )



    db.session.commit()



    return membership





# -------------------------------------------------
# Delete Customer
# -------------------------------------------------

def delete_customer(customer_id):


    customer = db.session.get(
        Customer,
        customer_id
    )


    if not customer:

        raise ValueError(
            "Customer not found."
        )



    for membership in customer.memberships:


        for installment in membership.installments:

            db.session.delete(
                installment
            )



        db.session.delete(
            membership
        )



    db.session.delete(
        customer
    )


    db.session.commit()