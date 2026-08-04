from flask_login import UserMixin

from database import db

from models.base import BaseModel


class User(
    BaseModel,
    UserMixin
):

    __tablename__ = "users"


    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )


    email = db.Column(
        db.String(120),
        unique=True
    )


    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


    mobile = db.Column(
        db.String(15)
    )


    approval_status = db.Column(
        db.String(20),
        default="PENDING"
    )


    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False
    )


    role = db.relationship(
        "Role",
        back_populates="users"
    )


    def get_id(self):

        return str(
            self.id
        )


    def __repr__(self):

        return self.username