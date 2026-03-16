from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify
from datetime import datetime

from utils.utils import login_required
from database.db import get_session
from database.models import Emocao


emocao_bp = Blueprint('emocao', __name__, template_folder='templates')


@emocao_bp.route('/emocoes')
@login_required
def emocoes():
    try:
        with get_session() as db:
            emocoes_lista = db.query(Emocao).filter_by(usuario_id=session.get('user_id')).order_by(Emocao.data.desc()).all()
    except Exception as e:
        print(e)
        flash('Não foi possiveil carregar a pagina!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('emocoes.html', emocoes=emocoes_lista)
    