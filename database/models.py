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
    ativo = Column(Boolean, nullable=False, default=True)
    email_confirmado = Column(Boolean, nullable=False, default=False)
    

class Evento(Base):
    __tablename__ = 'evento'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(400))
    data_hora = Column(DateTime, nullable=False)
    completado = Column(Boolean, nullable=False)
    color = Column(String(400))
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(400))
    data = Column(Date, nullable=False)
    evento_id = Column(Integer, ForeignKey("evento.id", ondelete="CASCADE"))
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)


class Emocao(Base):
    __tablename__ = 'emocao'

    id = Column(Integer, primary_key=True, autoincrement=True)
    humor = Column(String(30), nullable=False)
    descricao = Column(String(400))
    data = Column(Date, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False)


class Conteudo(Base):
    __tablename__ = 'conteudo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    descricao = Column(String(400))
    assunto = Column(String(100))
    tipo = Column(String(100), nullable=False)
    link = Column(String(400))
    ativo = Column(Boolean, nullable=False)
