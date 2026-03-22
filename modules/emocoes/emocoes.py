from flask import Blueprint, session, redirect, flash, render_template, url_for, request

from modules.utils import login_required
from database.db import get_session
from database.models import Emocao
from modules.emocoes.forms import EmocaoForm


emocao_bp = Blueprint('emocao', __name__, template_folder='templates')

emocoes_dict = {'feliz': '😃 Feliz', 'triste': '😕 Triste', 'entediado': '😐 Entediado', 'raiva': '😡 Raiva'}

@emocao_bp.route('/emocoes')
@login_required
def emocoes():
    form = EmocaoForm()
    form_ed = EmocaoForm() # Form de edição

    page = session.pop('page', None)
    if not page:
        page = 1
    per_page = 20
    offset = (page - 1) * per_page

    try:
        with get_session() as db:
            emocoes_lista = db.query(Emocao).filter_by(usuario_id=session.get('user_id')).order_by(Emocao.data.desc())
            total = emocoes_lista.count()
            total_pages = (total + per_page - 1) // per_page

            emocoes_lista = emocoes_lista.offset(offset).limit(per_page).all()
    except Exception as e:
        print(e)
        flash('Não foi possiveil carregar a pagina!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('emocoes.html', emocoes=emocoes_lista, form=form, emocoes_dict=emocoes_dict, form_ed=form_ed, total_pages=total_pages, page=page)
    

@emocao_bp.route('/paginacao_em', methods=['POST'])
@login_required
def paginacao_em():
    try:
        page = int(request.form.get('page'))
        if page < 1:
            page = 1
        session['page'] = page
    except Exception as e:
        print(e)
        flash('Não foi possivel processar a requisição', 'danger')

    return redirect(url_for('emocao.emocoes'))    


@emocao_bp.route('/cadastrar/emocao', methods=['POST'])
@login_required
def cadastrar_emocao():
    form = EmocaoForm()
    user_id = session.get('user_id')

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('emocao.emocoes'))

    humor = form.humor.data
    descricao = form.descricao.data
    data = form.data_field.data
    nova_emocao = Emocao(humor=humor, descricao=descricao, data=data, usuario_id=user_id)

    try:
        with get_session() as db:
            db.add(nova_emocao)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('emocao.emocoes'))

    flash('Item adicionado com sucesso!', 'success')
    return redirect(url_for('emocao.emocoes'))


@emocao_bp.route('/editar/emocao/<int:emocao_id>', methods=['POST'])
@login_required
def editar_emocao(emocao_id):
    form = EmocaoForm()
    user_id = session.get('user_id')

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('emocao.emocoes'))

    try:
        with get_session() as db:
            emocao = db.query(Emocao).filter_by(id=emocao_id).first()
            if not emocao:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('emocao.emocoes'))
            if emocao.usuario_id != user_id:
                flash('Não é possivel alterar o registro!', 'warning')
                return redirect(url_for('emocao.emocoes'))
            
            emocao.humor = form.humor.data
            emocao.descricao = form.descricao.data
            emocao.data = form.data_field.data
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('emocao.emocoes'))

    flash('Item editado com sucesso!', 'success')
    return redirect(url_for('emocao.emocoes'))



@emocao_bp.route('/excluir/emocao/<int:emocao_id>', methods=['POST'])
@login_required
def excluir_emocao(emocao_id):
    user_id = session.get('user_id')

    try:
        with get_session() as db:
            emocao = db.query(Emocao).filter_by(id=emocao_id).first()
            if not emocao:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('emocao.emocoes'))
            if emocao.usuario_id != user_id:
                flash('Não é possivel alterar o registro!', 'warning')
                return redirect(url_for('emocao.emocoes'))
            
            db.delete(emocao)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('emocao.emocoes'))

    flash('Item deletado com sucesso!', 'success')
    return redirect(url_for('emocao.emocoes'))