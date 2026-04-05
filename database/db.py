from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session as S
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()
db_name = os.environ.get('DB_NAME', 'database.db')

db = create_engine(f"sqlite:///{db_name}.db")
Session = sessionmaker(bind=db, expire_on_commit=False)


@contextmanager
def get_session():
    with Session() as session:
        try:
            yield session
            session.commit()   
        except:
            session.rollback()
            raise             
