from flask import Flask, render_template, session, redirect, flash
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

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

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.curdir), 'tmp','uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
IMAGE_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
os.makedirs(IMAGE_FOLDER, exist_ok=True)
IMG_PERFIL_FOLDER = os.path.join(UPLOAD_FOLDER, 'img-perfil')
os.makedirs(IMG_PERFIL_FOLDER, exist_ok=True)

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

@app.template_filter('format_date')
def format_date(value, formato='%d/%m/%Y'):
    if isinstance(value, date):
        return value.strftime(formato)
    return value

if __name__ == '__main__':
    Base.metadata.create_all(bind=db)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(agenda_bp)
    app.register_blueprint(emocao_bp)
    app.register_blueprint(feedbacks_bp)
    app.register_blueprint(conteudos_bp)
    app.run()
