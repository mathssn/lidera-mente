from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuario'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    senha = Column(String(255), nullable=False)

class Compromisso(Base):
    __tablename__ = 'compromisso'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    descricao = Column(String(100), nullable=False, unique=True)
    data_hora = Column(DateTime, nullable=False)
    completado = Column(Boolean, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    descricao = Column(String(100), nullable=False, unique=True)
    compromisso_id = Column(Integer, ForeignKey("compromisso.id"), nullable=False)


class Emoção(Base):
    __tablename__ = 'emoção'

    id = Column(Integer, primary_key=True, autoincrement=True)
    humor = Column(String(30), nullable=False)
    descricao = Column(String(100), nullable=False, unique=True)
    data = Column(Date, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)

