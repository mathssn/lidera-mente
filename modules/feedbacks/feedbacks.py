from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify
from datetime import datetime, timedelta

from modules.utils import login_required
from database.db import get_session
from database.models import Feedback, Evento
from modules.feedbacks.forms import FeedbackForm


feedbacks_bp = Blueprint('feedback', __name__, template_folder='templates')


@feedbacks_bp.route('/feedbacks')
@login_required
def feedbacks():
    form = FeedbackForm()
    form_ed = FeedbackForm()
    carregar_eventos_choices(form, session.get('user_id'))
    carregar_eventos_choices(form_ed, session.get('user_id'))

    page = session.pop('page', None)
    if not page:
        page = 1
    per_page = 20
    offset = (page - 1) * per_page

    try:
        with get_session() as db:
            eventos = db.query(Evento).filter_by(usuario_id=session.get('user_id')).all()
            eventos = {e.id: e for e in eventos}
            feedbacks_ = db.query(Feedback).filter_by(usuario_id=session.get('user_id')).order_by(Feedback.data.desc())
            total = feedbacks_.count()
            total_pages = (total + per_page - 1) // per_page

            feedbacks_ = feedbacks_.offset(offset).limit(per_page).all()
    except Exception as e:
        print(e)

    return render_template('feedbacks.html', feedbacks=feedbacks_, form=form, eventos=eventos, form_ed=form_ed)

@feedbacks_bp.route('/cadastrar/feedback', methods=['POST'])
@login_required
def cadastrar_feedback():
    form = FeedbackForm()
    user_id = session.get('user_id')
    carregar_eventos_choices(form, user_id)

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('feedback.feedbacks'))

    titulo = form.titulo.data
    descricao = form.descricao.data
    evento_id = form.evento_id.data
    data = form.data_field.data
    if not data:
        data = datetime.now().date()
    
    novo_feedback = Feedback(titulo=titulo, descricao=descricao, data=data, evento_id=evento_id, usuario_id=user_id)

    try:
        with get_session() as db:
            db.add(novo_feedback)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('feedback.feedbacks'))

    flash('Feedback adicionado com sucesso!', 'success')
    return redirect(url_for('feedback.feedbacks'))


@feedbacks_bp.route('/editar/feedback/<int:feedback_id>', methods=['POST'])
@login_required
def editar_feedback(feedback_id):
    form = FeedbackForm()
    user_id = session.get('user_id')
    carregar_eventos_choices(form, user_id)

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('feedback.feedbacks'))

    try:
        with get_session() as db:
            feedback = db.query(Feedback).filter_by(id=feedback_id).first()
            if not feedback:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('feedback.feedbacks'))
            if feedback.usuario_id != user_id:
                flash('Não é possível alterar o registro!', 'warning')
                return redirect(url_for('feedback.feedbacks'))

            feedback.titulo = form.titulo.data
            feedback.descricao = form.descricao.data
            feedback.evento_id = form.evento_id.data
            
            data = form.data_field.data
            if not data:
                data = datetime.now().date()
            feedback.data = data

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('feedback.feedbacks'))

    flash('Feedback editado com sucesso!', 'success')
    return redirect(url_for('feedback.feedbacks'))


@feedbacks_bp.route('/excluir/feedback/<int:feedback_id>', methods=['POST'])
@login_required
def excluir_feedback(feedback_id):
    user_id = session.get('user_id')

    try:
        with get_session() as db:
            feedback = db.query(Feedback).filter_by(id=feedback_id).first()
            if not feedback:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('feedback.feedbacks'))
            if feedback.usuario_id != user_id:
                flash('Não é possível alterar o registro!', 'warning')
                return redirect(url_for('feedback.feedbacks'))

            db.delete(feedback)

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('feedback.feedbacks'))

    flash('Feedback deletado com sucesso!', 'success')
    return redirect(url_for('feedback.feedbacks'))

def carregar_eventos_choices(form, user_id):
    hoje = datetime.now().date()
    v_dias_atras = hoje - timedelta(days=20) # 20 dias atras do dia atual
    with get_session() as db:
        eventos = db.query(Evento).filter_by(usuario_id=user_id).filter( Evento.data_hora >= v_dias_atras, Evento.data_hora <= hoje).all()
        form.evento_id.choices = [
            ("", "-"),
            *[(e.id, f"{e.titulo} em {e.data_hora.date().strftime('%d/%m/%Y')}") for e in eventos]
        ]