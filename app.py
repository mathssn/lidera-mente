from flask import Flask, render_template, session

from database.db import db, get_session
from database.models import Base
from database.insert import *
from modules.utils import login_required

from modules.usuario.usuarios import usuarios_bp
from modules.agenda.agenda import agenda_bp
from modules.emocoes.emocoes import emocao_bp
from modules.feedbacks.feedbacks import feedbacks_bp

app = Flask(__name__)
app.secret_key = '1234'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


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
    app.run(debug=True)