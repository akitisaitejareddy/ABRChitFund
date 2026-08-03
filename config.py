import os
from dotenv import load_dotenv


load_dotenv()


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "abr-default-secret"
    )


    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///abrchitfund.db"
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = False