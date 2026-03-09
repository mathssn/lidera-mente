from database.models import *

from sqlalchemy import event
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash


@event.listens_for(Usuario.__table__, "after_create")
def insert_usuario(target, connection, **kw):
    connection.execute(
        Usuario.__table__.insert(),
            ({"nome": 'admin', "email": 'admin@gmail.com', "senha": generate_password_hash('1234'), "data_nascimento": date(2000, 1, 1)})
        )
    
    connection.execute(
        Usuario.__table__.insert(),
            ({"nome": 'teste', "email": 'teste@gmail.com', "senha": generate_password_hash('1234'), "data_nascimento": date(2000, 1, 1)})
        )