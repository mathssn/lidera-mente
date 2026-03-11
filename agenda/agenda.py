from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify
from datetime import datetime
import calendar

from utils.utils import login_required
from database.db import get_session
from database.models import Evento

from agenda.forms import EventoForm

agenda_bp = Blueprint('agenda', __name__, template_folder='templates')


@agenda_bp.route('/agenda')
@login_required
def agenda():
    form_evento = EventoForm()
    user_id = session.get('user_id')

    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    mes_atual = 1
    
    try:
        with get_session() as db:
            eventos = db.query(Evento).filter_by(usuario_id=user_id).limit(10).all()
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect('/')

    return render_template('agenda.html', eventos=eventos, form_evento=form_evento, data=[ano_atual, mes_atual])


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
    calendar.setfirstweekday(calendar.SUNDAY)
    semanas = calendar.monthcalendar(ano, mes)

    # mês anterior
    if mes == 1:
        ano_ant = ano - 1
        mes_ant = 12
    else:
        ano_ant = ano
        mes_ant = mes - 1

    ultimo_dia_mes_ant = calendar.monthrange(ano_ant, mes_ant)[1]

    # preencher início
    primeira_semana = semanas[0]
    zeros_inicio = primeira_semana.count(0)

    for i in range(zeros_inicio):
        primeira_semana[i] = ultimo_dia_mes_ant - zeros_inicio + i + 1

    # preencher final
    contador = 1
    ultima_semana = semanas[-1]

    for i in range(len(ultima_semana)):
        if ultima_semana[i] == 0:
            ultima_semana[i] = contador
            contador += 1

    print(semanas)

    return jsonify({
        "semanas": semanas,
        "ano": ano,
        "mes": mes
    })
