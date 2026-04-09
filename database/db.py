from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_NAME = os.getenv("MYSQL_DATABASE")
DATABASE_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

def get_engine_local():
    engine = create_engine(f'mysql+mysqlconnector://root:{DATABASE_ROOT_PASSWORD}@localhost:3306')

    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))

    engine = create_engine(f'mysql+mysqlconnector://root:{DATABASE_ROOT_PASSWORD}@localhost:3306/{DATABASE_NAME}', pool_pre_ping=True, pool_recycle=1800)
    return engine

def get_engine_docker():
    # Cria engine conectando direto ao banco do container "db"
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=1800
    )
    return engine


db = get_engine_docker()
SessionLocal = sessionmaker(
    bind=db,
    expire_on_commit=False
)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()