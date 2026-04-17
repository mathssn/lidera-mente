from flask import Flask, render_template, session, redirect, flash
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import os
import time

from database.db import db, get_session
from database.models import Base, Evento
from database.insert import *
from modules.utils import login_required

from modules.usuario.usuarios import usuarios_bp
from modules.agenda.agenda import agenda_bp
from modules.emocoes.emocoes import emocao_bp
from modules.feedbacks.feedbacks import feedbacks_bp
from modules.conteudos.conteudos import conteudos_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    agora = datetime.now()
    limite = agora + timedelta(days=5)

    try:
        with get_session() as db:
            # Eventos dos proximos 5 dias
            eventos = db.query(Evento).filter(Evento.data_hora.between(agora, limite)).filter_by(usuario_id=session.get('user_id')).order_by(Evento.data_hora.asc()).all()
    except Exception as e:
        print(e)
        flash('Falah ao carregar eventos', 'warning')
        eventos = []

    return render_template('dashboard.html', eventos=eventos)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/apoio')
def apoio():
    return render_template('apoio.html')

@app.template_filter('format_date')
def format_date(value, formato='%d/%m/%Y'):
    if isinstance(value, date):
        return value.strftime(formato)
    return value

# Retry para esperar o banco subir
for i in range(10):
    try:
        print(f"Tentando conectar ao banco... ({i+1}/10)")
        Base.metadata.create_all(bind=db)
        print("Conectado ao banco com sucesso!")
        break
    except Exception as e:
        print("Erro ao conectar no banco:", e)
        time.sleep(3)
else:
    print("Não foi possível conectar ao banco.")
    exit(1)

app.register_blueprint(usuarios_bp)
app.register_blueprint(agenda_bp)
app.register_blueprint(emocao_bp)
app.register_blueprint(feedbacks_bp)
app.register_blueprint(conteudos_bp)
if __name__ == '__main__':
    app.run(debug=True, port=4000)