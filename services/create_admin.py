from app import create_app

from database import db

from models.role import Role

from models.user import User

from utils.password import hash_password



app = create_app()



with app.app_context():


    admin_role = Role.query.filter_by(
        name="ADMIN"
    ).first()



    if not admin_role:

        print(
            "ADMIN role does not exist"
        )

        exit()



    existing_admin = User.query.filter_by(
        username="admin"
    ).first()



    if existing_admin:

        print(
            "Admin already exists"
        )

        exit()



    admin = User(

        username="admin",

        email="admin@abrchitfund.com",

        password_hash=hash_password(
            "Admin@12345"
        ),

        role_id=admin_role.id,

        approval_status="APPROVED"

    )


    db.session.add(admin)

    db.session.commit()



    print(
        "Admin account created successfully"
    )