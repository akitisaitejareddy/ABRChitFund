from models.user import User
from utils.password import check_password


def authenticate_user(username, password):
    """
    Authenticate user credentials.

    Returns:
        User object if successful
        None if authentication fails
    """


    user = User.query.filter_by(
        username=username
    ).first()


    if not user:
        return None


    if not check_password(
        password,
        user.password_hash
    ):
        return None


    if not user.is_active:
        return None


    if user.approval_status != "APPROVED":
        return None


    return user



def get_user_role(user):
    """
    Returns user role name.
    """

    if not user or not user.role:

        return None


    return user.role.name