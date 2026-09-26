import json

from flask import request
from flask_login import current_user

from database import db
from models.audit_log import AuditLog


def _serialize_values(values):
    """
    Convert a dictionary into JSON safely.
    """

    if values is None:
        return None

    try:
        return json.dumps(
            values,
            default=str
        )
    except (TypeError, ValueError):
        return json.dumps(
            {"value": str(values)}
        )


def log_action(
    action,
    entity_type,
    entity_id=None,
    description=None,
    old_values=None,
    new_values=None
):
    """
    Create an audit log entry.

    Parameters:
        action:
            CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.

        entity_type:
            CUSTOMER, GROUP, PAYMENT, AUCTION, USER, etc.

        entity_id:
            ID of the affected record.

        description:
            Human-readable description.

        old_values:
            Values before the change.

        new_values:
            Values after the change.
    """

    try:

        user_id = None

        if (
            current_user
            and current_user.is_authenticated
        ):
            user_id = current_user.id

        ip_address = None

        if request:
            ip_address = (
                request.headers.get(
                    "X-Forwarded-For"
                )
                or request.remote_addr
            )

        audit = AuditLog(

            user_id=user_id,

            action=str(
                action
            ).upper(),

            entity_type=str(
                entity_type
            ).upper(),

            entity_id=entity_id,

            description=description,

            old_values=_serialize_values(
                old_values
            ),

            new_values=_serialize_values(
                new_values
            ),

            ip_address=ip_address

        )

        db.session.add(
            audit
        )

        db.session.commit()

        return audit

    except Exception as error:

        db.session.rollback()

        print(
            f"Audit logging failed: {error}"
        )

        return None