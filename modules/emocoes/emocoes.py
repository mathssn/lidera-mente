from flask import Blueprint, session, redirect, flash, render_template, url_for, request

from modules.utils import login_required
from database.db import get_session
from database.models import Emocao
from modules.emocoes.forms import EmocaoForm


emocao_bp = Blueprint('emocao', __name__, template_folder='templates')

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
            ems = []
            for e in emocoes_lista:
                try:
                    emoji, humor = e.humor.split('|', 1)
                except:
                    emoji = e.humor
                    humor = e.humor
                e_dict = {
                    "id": e.id,
                    "emoji": emoji,
                    "humor": humor,
                    "descricao": e.descricao,
                    "data": e.data
                }
                ems.append(e_dict)
    except Exception as e:
        print(e)
        flash('Não foi possiveil carregar a pagina!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('emocoes.html', emocoes=ems, form=form, form_ed=form_ed, total_pages=total_pages, page=page)
    

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
    emoji = form.emoji.data
    descricao = form.descricao.data
    data = form.data_field.data

    humor_completo = f"{emoji}|{humor}"
    nova_emocao = Emocao(humor=humor_completo, descricao=descricao, data=data, usuario_id=user_id)

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
            
            humor = form.humor.data
            emoji = form.emoji.data
            humor_completo = f"{emoji}|{humor}"
            emocao.humor = humor_completo
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