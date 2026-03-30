from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify, request, send_from_directory, abort, current_app
from datetime import datetime
import os
import glob

from modules.utils import login_required
from database.db import get_session
from database.models import Conteudo

from modules.conteudos.forms import ConteudoForm

conteudos_bp = Blueprint('conteudos', __name__, template_folder='templates')


@conteudos_bp.route('/relaxamento')
@login_required
def relaxamento():
    try:
        with get_session() as db:
            conteudos = db.query(Conteudo).filter_by(tipo='relaxamento').filter(not(Conteudo.ativo)).all()
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('relaxamento.html', conteudos=conteudos)


@conteudos_bp.route('/conteudos')
@login_required
def conteudos():
    try:
        with get_session() as db:
            conteudos_ = db.query(Conteudo).filter_by(tipo='material').filter(Conteudo.ativo).all()
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('conteudos.html', conteudos=conteudos_)


@conteudos_bp.route('/imagem/<int:id>')
def carregar_imagem(id):
    pasta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images')
    
    padrao = os.path.join(pasta, f"{id}.*")
    arquivos = glob.glob(padrao)

    if not arquivos:
        abort(404)

    # Pega o primeiro arquivo encontrado
    caminho_arquivo = arquivos[0]
    nome_arquivo = os.path.basename(caminho_arquivo)

    return send_from_directory(pasta, nome_arquivo)

# @conteudos_bp.route('/cadastrar/conteudo/<tipo>', methods=['POST'])
# @login_required
# def cadastrar_conteudo(tipo):
#     if session.get('nome') != 'admin':
#         return redirect('/')
    
#     form = ConteudoForm()

#     if not form.validate_on_submit():
#         flash('Insira dados válidos!', 'danger')
#         return redirect(url_for('dashboard'))

#     titulo=form.titulo.data,
#     descricao=form.descricao.data,
#     assunto=form.assunto.data,
#     tipo_=tipo,
#     link=form.link.data,
#     ativo = False
#     if form.ativo.data == 'ativo':
#         ativo = True
    
#     novo_conteudo = Conteudo(titulo=titulo, descricao=descricao, assunto=assunto, tipo=tipo_, link=link, ativo=ativo)

#     try:
#         with get_session() as db:
#             db.add(novo_conteudo)
#     except Exception as e:
#         print(e)
#         flash('Erro inesperado!', 'danger')
#         return redirect(url_for('dashboard'))

#     flash('Conteúdo adicionado com sucesso!', 'success')
#     return redirect(url_for('dashboard'))

# @conteudos_bp.route('/editar/conteudo/<int:conteudo_id>', methods=['POST'])
# @login_required
# def editar_conteudo(conteudo_id):
#     if session.get('nome') != 'admin':
#         return redirect('/')
    
#     form = ConteudoForm()

#     if not form.validate_on_submit():
#         flash('Insira dados válidos!', 'danger')
#         return redirect(url_for('dashboard'))

#     try:
#         with get_session() as db:
#             conteudo = db.query(Conteudo).filter_by(id=conteudo_id).first()

#             if not conteudo:
#                 flash('Registro não encontrado!', 'danger')
#                 return redirect(url_for('dashboard'))

#             conteudo.titulo = form.titulo.data
#             conteudo.descricao = form.descricao.data
#             conteudo.assunto = form.assunto.data
#             conteudo.tipo = form.tipo.data
#             conteudo.link = form.link.data
#             if form.ativo.data == 'ativo':
#                 conteudo.ativo = True
#             else:
#                 conteudo.ativo = False

#     except Exception as e:
#         print(e)
#         flash('Erro inesperado!', 'danger')
#         return redirect(url_for('dashboard'))

#     flash('Conteúdo editado com sucesso!', 'success')
#     return redirect(url_for('dashboard'))

# @conteudos_bp.route('/excluir/conteudo/<int:conteudo_id>', methods=['POST'])
# @login_required
# def excluir_conteudo(conteudo_id):
#     if session.get('nome') != 'admin':
#         return redirect('/')

#     try:
#         with get_session() as db:
#             conteudo = db.query(Conteudo).filter_by(id=conteudo_id).first()
#             if not conteudo:
#                 flash('Registro não encontrado!', 'danger')
#                 return redirect(url_for('dashboard'))
#             db.delete(conteudo)
#     except Exception as e:
#         print(e)
#         flash('Erro inesperado!', 'danger')
#         return redirect(url_for('dashboard'))

#     flash('Conteúdo deletado com sucesso!', 'success')
#     return redirect(url_for('dashboard'))