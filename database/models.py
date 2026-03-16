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

class Evento(Base):
    __tablename__ = 'evento'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(400))
    data_hora = Column(DateTime, nullable=False)
    completado = Column(Boolean, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(400))
    compromisso_id = Column(Integer, ForeignKey("evento.id"), nullable=False)


class Emocao(Base):
    __tablename__ = 'emocao'

    id = Column(Integer, primary_key=True, autoincrement=True)
    humor = Column(String(30), nullable=False)
    descricao = Column(String(400))
    data = Column(Date, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id"), nullable=False)


"""
INSERT INTO emocao (humor, descricao, data, usuario_id) VALUES ('Feliz', 'aa', '2026-03-14', 2), ('Cansado', 'aa', '2026-03-13', 2);
"""