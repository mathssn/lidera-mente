from database.models import *

from sqlalchemy import event
from datetime import date
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

@event.listens_for(Usuario.__table__, "after_create")
def insert_usuario(target, connection, **kw):
    connection.execute(
        Usuario.__table__.insert(),
            ({"nome": 'Admin', "email": os.environ.get('ADMIN_EMAIL'), "senha": generate_password_hash(os.environ.get('ADMIN_PASSWORD')), "data_nascimento": date(2000, 1, 1), "email_confirmado": True})
        )