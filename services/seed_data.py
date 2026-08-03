from app import create_app
from database import db
from models.role import Role


app = create_app()


with app.app_context():

    default_roles = [
        "ADMIN",
        "EMPLOYEE",
        "SUBSCRIBER"
    ]


    for role_name in default_roles:

        existing_role = Role.query.filter_by(
            name=role_name
        ).first()


        if not existing_role:

            role = Role(
                name=role_name,
                description=f"{role_name} role"
            )

            db.session.add(role)


    db.session.commit()


print("Default roles created successfully")