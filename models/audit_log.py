from database import db

from models.base import BaseModel


class AuditLog(BaseModel):

    __tablename__ = "audit_logs"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "users.id"
        ),
        nullable=True
    )

    action = db.Column(
        db.String(20),
        nullable=False
    )

    entity_type = db.Column(
        db.String(100),
        nullable=False
    )

    entity_id = db.Column(
        db.Integer,
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    old_values = db.Column(
        db.Text,
        nullable=True
    )

    new_values = db.Column(
        db.Text,
        nullable=True
    )

    ip_address = db.Column(
        db.String(45),
        nullable=True
    )

    user = db.relationship(
        "User",
        backref="audit_logs"
    )

    def __repr__(self):

        return (
            f"<AuditLog "
            f"{self.action} "
            f"{self.entity_type} "
            f"{self.entity_id}>"
        )