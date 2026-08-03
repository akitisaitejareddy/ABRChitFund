from database import db

from models.base import BaseModel


class Permission(BaseModel):

    __tablename__ = "permissions"


    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )


    description = db.Column(
        db.String(255)
    )