
import json

from sqlalchemy import event
from sqlalchemy import inspect

from flask import has_request_context

from flask_login import current_user

from models.base import BaseModel
from models.audit_log import AuditLog
from flask import has_request_context, request


# ============================================================
# SENSITIVE FIELDS
# ============================================================

SENSITIVE_FIELDS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "secret_key"
}


# ============================================================
# VALUE CONVERSION
# ============================================================

def serialize_value(value):

    if value is None:
        return None

    if hasattr(value, "isoformat"):

        return value.isoformat()

    if isinstance(
        value,
        (str, int, float, bool)
    ):

        return value

    return str(value)


# ============================================================
# MODEL TO DICTIONARY
# ============================================================

def model_to_dict(instance):

    data = {}

    for column in instance.__table__.columns:

        field_name = column.name

        if field_name in SENSITIVE_FIELDS:

            continue

        try:

            value = getattr(
                instance,
                field_name
            )

            data[field_name] = serialize_value(
                value
            )

        except Exception:

            continue

    return data


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user_id():

    if not has_request_context():

        return None

    try:

        if current_user.is_authenticated:

            return current_user.id

    except Exception:

        pass

    return None


# ============================================================
# IP ADDRESS
# ============================================================

def get_ip_address():

    if not has_request_context():

        return None

    try:

        return request.remote_addr

    except Exception:

        return None


# ============================================================
# CREATE AUDIT RECORD
# ============================================================

def create_audit_record(
    connection,
    action,
    target,
    old_values=None,
    new_values=None
):

    # Never audit the audit table itself

    if isinstance(
        target,
        AuditLog
    ):

        return

    user_id = get_current_user_id()

    entity_type = (
        target.__class__.__name__
    )

    entity_id = getattr(
        target,
        "id",
        None
    )

    description = (
        f"{action} "
        f"{entity_type}"
    )

    if entity_id is not None:

        description += (
            f" #{entity_id}"
        )

    values = {

        "user_id":
            user_id,

        "action":
            action,

        "entity_type":
            entity_type,

        "entity_id":
            entity_id,

        "description":
            description,

        "old_values":
            json.dumps(
                old_values,
                default=str
            )
            if old_values is not None
            else None,

        "new_values":
            json.dumps(
                new_values,
                default=str
            )
            if new_values is not None
            else None

    }

    connection.execute(
        AuditLog.__table__.insert().values(
            **values
        )
    )


# ============================================================
# AFTER INSERT
# ============================================================

@event.listens_for(
    BaseModel,
    "after_insert",
    propagate=True
)
def audit_after_insert(
    mapper,
    connection,
    target
):

    if isinstance(
        target,
        AuditLog
    ):

        return

    new_values = model_to_dict(
        target
    )

    create_audit_record(

        connection,

        "CREATE",

        target,

        new_values=new_values

    )


# ============================================================
# AFTER UPDATE
# ============================================================

@event.listens_for(
    BaseModel,
    "after_update",
    propagate=True
)
def audit_after_update(
    mapper,
    connection,
    target
):

    if isinstance(
        target,
        AuditLog
    ):

        return

    state = inspect(
        target
    )

    old_values = {}
    new_values = {}

    for column in mapper.column_attrs:

        field_name = column.key

        if field_name in SENSITIVE_FIELDS:

            continue

        history = state.attrs[
            field_name
        ].history

        if not history.has_changes():

            continue

        old_value = None
        new_value = None

        if history.deleted:

            old_value = history.deleted[0]

        if history.added:

            new_value = history.added[0]

        old_values[
            field_name
        ] = serialize_value(
            old_value
        )

        new_values[
            field_name
        ] = serialize_value(
            new_value
        )

    if not old_values and not new_values:

        return

    create_audit_record(

        connection,

        "UPDATE",

        target,

        old_values=old_values,

        new_values=new_values

    )


# ============================================================
# AFTER DELETE
# ============================================================

@event.listens_for(
    BaseModel,
    "after_delete",
    propagate=True
)
def audit_after_delete(
    mapper,
    connection,
    target
):

    if isinstance(
        target,
        AuditLog
    ):

        return

    old_values = model_to_dict(
        target
    )

    create_audit_record(

        connection,

        "DELETE",

        target,

        old_values=old_values

    )

