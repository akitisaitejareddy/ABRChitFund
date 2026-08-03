from database import db

from models.base import BaseModel


class Role(BaseModel):

    __tablename__ = "roles"


    name = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )


    description = db.Column(
        db.String(255)
    )


    users = db.relationship(
        "User",
        back_populates="role"
    )


    def __repr__(self):

        return self.name