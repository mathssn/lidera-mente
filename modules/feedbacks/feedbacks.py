from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify
from datetime import datetime, timedelta
import calendar

from modules.utils import login_required
from database.db import get_session
from database.models import Feedback, Evento


feedbacks_bp = Blueprint('feedback', __name__, template_folder='templates')


@feedbacks_bp.route('/feedbacks')
@login_required
def feedbacks():
    hoje = datetime.now().date()
    v_dias_atras = hoje - timedelta(days=20) # 20 dias atras do dia atual

    page = session.pop('page', None)
    if not page:
        page = 1
    per_page = 20
    offset = (page - 1) * per_page

    try:
        with get_session() as db:
            eventos = db.query(Evento).filter_by(usuario_id=session.get('user_id')).filter(
                Evento.data_hora >= v_dias_atras, Evento.data_hora <= hoje
            ).all()
            feedbacks_ = db.query()
    except Exception as e:
        print(e)

    return render_template('feedbacks.html', eventos=eventos)
