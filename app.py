from flask import Flask, render_template, session

from database.db import db, get_session
from database.models import Base
from database.insert import *
from utils.utils import login_required

from usuario.usuarios import usuarios_bp
from agenda.agenda import agenda_bp
from emocoes.emocoes import emocao_bp

app = Flask(__name__)
app.secret_key = '1234'

@app.route('/')
def index():
    print(session.get('user_id'))
    print(session.get('nome'))
    print(session.get('sobrenome'))
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
    app.run(debug=True)