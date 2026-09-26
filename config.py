import os
if os.environ.get("VERCEL"):
    os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "sqlite:////tmp/abrchitfund.db")
import os

basedir = os.path.abspath(os.path.dirname(__file__))
if os.environ.get('VERCEL'):
    db_path = '/tmp/abrchitfund.db'
else:
    db_path = os.path.join(basedir, 'instance', 'abrchitfund.db')

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