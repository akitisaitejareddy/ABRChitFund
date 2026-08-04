from app import create_app

from database import db

from models.role import Role
from models.user import User

from utils.password import hash_password



app = create_app()



def create_admin():

    with app.app_context():


        admin_role = Role.query.filter_by(
            name="ADMIN"
        ).first()


        if not admin_role:

            print(
                "ADMIN role does not exist. Run seed_data first."
            )

            return



        existing_admin = User.query.filter_by(
            username="admin"
        ).first()



        if existing_admin:

            print(
                "Admin user already exists."
            )

            return



        admin_user = User(

            username="admin",

            email="admin@abrchitfund.com",

            password_hash=hash_password(
                "Admin@12345"
            ),

            mobile=None,

            approval_status="APPROVED",

            role_id=admin_role.id

        )


        db.session.add(
            admin_user
        )


        db.session.commit()


        print(
            "Admin user created successfully."
        )



if __name__ == "__main__":

    create_admin()