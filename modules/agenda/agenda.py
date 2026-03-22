from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify
from datetime import datetime
import calendar

from modules.utils import login_required
from database.db import get_session
from database.models import Evento, Tag

from modules.agenda.forms import EventoForm, TagForm

agenda_bp = Blueprint('agenda', __name__, template_folder='templates')

meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

@agenda_bp.route('/agenda')
@login_required
def agenda():
    form = EventoForm()
    form_ed = EventoForm()
    
    ano = session.pop('ano', None)
    if not ano:
        ano = datetime.now().year
    mes = session.pop('mes', None)
    if not mes:
        mes = datetime.now().month

    try:
        with get_session() as db:
            tags = db.query(Tag).filter_by(usuario_id=session.get('user_id')).all()
    except Exception as e:
        print('e')
        flash('Erro inesperado!', 'danger')
        return redirect('/')

    return render_template('agenda.html', form=form, form_ed=form_ed, data=[ano, mes], tags=tags)


@agenda_bp.route('/cadastrar/evento', methods=['POST'])
@login_required
def cadastrar_evento():
    form = EventoForm()
    user_id = session.get('user_id')

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('agenda.agenda'))
    
    titulo = form.titulo.data
    descricao = form.descricao.data
    data_hora = form.data_hora.data
    novo_evento = Evento(titulo=titulo, descricao=descricao, data_hora=data_hora, completado=False, usuario_id=user_id)
    try:
        with get_session() as db:
            db.add(novo_evento)
            session['mes'] = data_hora.month
            session['ano'] = data_hora.year
    except Exception as e:
        session.pop('mes', None)
        session.pop('ano', None)
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.agenda'))

    flash('Evento adicionado com sucesso!', 'success')
    return redirect(url_for('agenda.agenda'))


@agenda_bp.route('/editar/evento/<int:evento_id>', methods=['POST'])
@login_required
def editar_evento(evento_id):
    form = EventoForm()
    user_id = session.get('user_id')

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('agenda.agenda'))

    try:
        with get_session() as db:
            evento = db.query(Evento).filter_by(id=evento_id).first()
            if not evento:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('agenda.agenda'))
            if evento.usuario_id != user_id:
                flash('Não é possível alterar o registro!', 'warning')
                return redirect(url_for('agenda.agenda'))

            evento.titulo = form.titulo.data
            evento.descricao = form.descricao.data
            evento.data_hora = form.data_hora.data

            session['mes'] = evento.data_hora.month
            session['ano'] = evento.data_hora.year
    except Exception as e:
        session.pop('mes', None)
        session.pop('ano', None)
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.agenda'))

    flash('Evento editado com sucesso!', 'success')
    return redirect(url_for('agenda.agenda'))


@agenda_bp.route('/excluir/evento/<int:evento_id>', methods=['POST'])
@login_required
def excluir_evento(evento_id):
    user_id = session.get('user_id')

    try:
        with get_session() as db:
            evento = db.query(Evento).filter_by(id=evento_id).first()
            if not evento:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('agenda.agenda'))
            if evento.usuario_id != user_id:
                flash('Não é possível alterar o registro!', 'warning')
                return redirect(url_for('agenda.agenda'))

            session['mes'] = evento.data_hora.month
            session['ano'] = evento.data_hora.year
            db.delete(evento)
    except Exception as e:
        session.pop('mes', None)
        session.pop('ano', None)
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.agenda'))

    flash('Evento deletado com sucesso!', 'success')
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


@agenda_bp.route('/tags')
@login_required
def tags():
    form = TagForm()
    form_ed = TagForm()
    
    try:
        with get_session() as db:
            tags_ = db.query(Tag).filter_by(usuario_id=session.get('user_id')).all()
    except Exception as e:
        print('e')
        flash('Erro inesperado!', 'danger')
        return redirect('/')
    
    return render_template('tags.html', tags=tags_, form=form, form_ed=form_ed)


@agenda_bp.route('/cadastrar/tag', methods=['POST'])
@login_required
def cadastrar_tag():
    form = TagForm()
    user_id = session.get('user_id')

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('agenda.tags'))

    nome = form.nome.data
    color = form.color.data

    nova_tag = Tag(nome=nome, color=color, usuario_id=user_id)

    try:
        with get_session() as db:
            db.add(nova_tag)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.tags'))

    flash('Tag adicionada com sucesso!', 'success')
    return redirect(url_for('agenda.tags'))


@agenda_bp.route('/editar/tag/<int:tag_id>', methods=['POST'])
@login_required
def editar_tag(tag_id):
    form = TagForm()
    user_id = session.get('user_id')

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('agenda.tags'))

    try:
        with get_session() as db:
            tag = db.query(Tag).filter_by(id=tag_id).first()

            if not tag:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('agenda.tags'))

            if tag.usuario_id != user_id:
                flash('Não é possível alterar o registro!', 'warning')
                return redirect(url_for('agenda.tags'))

            tag.nome = form.nome.data
            tag.color = form.color.data

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.tags'))

    flash('Tag editada com sucesso!', 'success')
    return redirect(url_for('agenda.tags'))


@agenda_bp.route('/excluir/tag/<int:tag_id>', methods=['POST'])
@login_required
def excluir_tag(tag_id):
    user_id = session.get('user_id')

    try:
        with get_session() as db:
            tag = db.query(Tag).filter_by(id=tag_id).first()

            if not tag:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('agenda.tags'))

            if tag.usuario_id != user_id:
                flash('Não é possível alterar o registro!', 'warning')
                return redirect(url_for('agenda.tags'))

            db.delete(tag)

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('agenda.tags'))

    flash('Tag deletada com sucesso!', 'success')
    return redirect(url_for('agenda.tags'))