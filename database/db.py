from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session as S
from contextlib import contextmanager
from dotenv import load_dotenv
import os

db = create_engine("sqlite:///database/db.db")

load_dotenv()
db_name = os.environ.get('DB_NAME')
username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')

db = create_engine(f"mysql+mysqlconnector://{username}:{password}@localhost:3306")

with db.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))

db = create_engine(f"mysql+mysqlconnector://{username}:{password}@localhost:3306/{db_name}", pool_pre_ping=True, pool_recycle=1800)
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
