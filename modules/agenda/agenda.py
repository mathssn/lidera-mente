from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify
from datetime import datetime
import calendar

from modules.utils import login_required
from database.db import get_session
from database.models import Evento

from modules.agenda.forms import EventoForm

agenda_bp = Blueprint('agenda', __name__, template_folder='templates')

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

@agenda_bp.route('/agenda')
@login_required
def agenda():
    form_evento = EventoForm()

    ano_atual = datetime.now().year
    mes_atual = datetime.now().month

    return render_template('agenda.html', form_evento=form_evento, data=[ano_atual, mes_atual])


@agenda_bp.route('/cadastrar/evento', methods=['POST'])
@login_required
def cadastrar_evento():
    form_evento = EventoForm()
    user_id = session.get('user_id')

    if not form_evento.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('agenda.agenda'))
    
    titulo = form_evento.titulo.data
    descricao = form_evento.descricao.data
    data_hora = form_evento.data_hora.data
    novo_evento = Evento(titulo=titulo, descricao=descricao, data_hora=data_hora, completado=False, usuario_id=user_id)
    try:
        with get_session() as db:
            db.add(novo_evento)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.agenda'))

    flash('Evento adicionado com sucesso!', 'success')
    return redirect(url_for('agenda.agenda'))


@agenda_bp.route('/calendario/<int:ano>/<int:mes>')
@login_required
def calendario(ano, mes):
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)

    try:
        mes_inicio = mes-1
        ano_inicio = ano
        if mes_inicio <= 0:
            mes_inicio = 12
            ano_inicio = ano-1
        mes_fim = mes+2
        ano_fim = ano
        if mes_fim > 12:
            mes_fim = mes_fim - 12
            ano_fim = ano+1
        with get_session() as db:
            eventos = db.query(Evento).filter_by(usuario_id=session.get('user_id')).filter(Evento.data_hora >= datetime(ano_inicio, mes_inicio, 1), Evento.data_hora < datetime(ano_fim, mes_fim, 1)).all()
            eventos = [
                {'id': e.id, 'titulo': e.titulo, 'descricao': e.descricao, 'data_hora': e.data_hora.isoformat(), 'completado': e.completado, 'usuario_id': e.usuario_id} for e in eventos
            ]
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect('/')


    semanas = []
    semana = []

    for dia in cal.itermonthdates(ano, mes):
        semana.append(dia.strftime("%d/%m/%Y"))

        if len(semana) == 7:
            semanas.append(semana)
            semana = []

    return jsonify({
        "semanas": semanas,
        "ano": ano,
        "mes": mes,
        "mes_nome": meses[mes-1],
        "eventos": eventos
    })


@agenda_bp.route('/checar/evento/<int:evento_id>', methods=['POST'])
@login_required
def checar_evento(evento_id):
    try:
        with get_session() as db:
            evento = db.query(Evento).filter_by(id=evento_id).first()
            if not evento:
                flash('Não foi possivel checar o evento!', 'danger')
                return redirect(url_for('agenda.agenda'))
            if evento.usuario_id != session.get('user_id'):
                flash('Não foi possivel checar o evento!', 'danger')
                return redirect(url_for('index'))
            evento.completado = not evento.completado
    except:
        flash('Não foi possivel checar o evento!', 'danger')
        return redirect(url_for('agenda.agenda'))
    
    return 200

