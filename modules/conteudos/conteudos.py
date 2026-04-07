from flask import Blueprint, session, redirect, flash, render_template, url_for, jsonify, request, abort, Response
from PIL import Image
import io

from modules.utils import login_required
from database.db import get_session
from database.models import Conteudo

from modules.conteudos.forms import ConteudoForm

conteudos_bp = Blueprint('conteudos', __name__, template_folder='templates')


@conteudos_bp.route('/relaxamento')
@login_required
def relaxamento():
    form = ConteudoForm()
    form_ed = ConteudoForm()
    try:
        with get_session() as db:
            conteudos = db.query(Conteudo).filter_by(tipo='relaxamento').all()
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('relaxamento.html', conteudos=conteudos, form=form, form_ed=form_ed)


@conteudos_bp.route('/conteudos')
@login_required
def conteudos():
    form = ConteudoForm()
    form_ed = ConteudoForm()
    try:
        with get_session() as db:
            conteudos_ = db.query(Conteudo).filter_by(tipo='material').all()
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('conteudos.html', conteudos=conteudos_, form=form, form_ed=form_ed)


@conteudos_bp.route('/imagem/<int:conteudo_id>')
def carregar_imagem(conteudo_id):
    try:
        with get_session() as session_db:
            conteudo = session_db.query(Conteudo).filter_by(id=conteudo_id).first()

            if not conteudo or not conteudo.img:
                abort(404)

            return Response(conteudo.img, mimetype=conteudo.img_mimetype)
    except Exception as e:
        print(e)
        abort(404)


@conteudos_bp.route('/upload-imagem/<int:conteudo_id>', methods=['POST'])
@login_required
def upload_imagem(conteudo_id):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect(url_for('dashboard'))
    
    file = request.files.get('imagem')

    if not file or file.filename == "":
        flash('Selecione uma imagem', 'warning')
        return redirect(url_for('dashboard'))

    try:
        image = Image.open(file)

        if image.format not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
            flash('Formato inválido. Use JPG, PNG ou WEBP.', 'warning')
            return jsonify({'sucesso': False})
        
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        img_io = io.BytesIO()

        image.save(img_io, format='JPEG', quality=100, optimize=True)
        img_io.seek(0)

        with get_session() as session_db:
            conteudo = session_db.query(Conteudo).filter_by(id=conteudo_id).first()

            if not conteudo:
                flash('Conteúdo não encontrado!', 'danger')
                return redirect(url_for('dashboard'))
            tipo = conteudo.tipo

            conteudo.img = img_io.read()
            conteudo.img_mimetype = 'image/jpeg'

    except Exception as e:
        print(e)
        flash('Erro ao enviar imagem!', 'danger')
        if tipo == 'material':
            return redirect(url_for('conteudos.conteudos'))
        elif tipo == 'relaxamento':
            return redirect(url_for('conteudos.relaxamento'))
        return redirect(url_for('dashboard'))

    flash('Imagem alterada com sucesso!', 'success')
    if tipo == 'material':
        return redirect(url_for('conteudos.conteudos'))
    elif tipo == 'relaxamento':
        return redirect(url_for('conteudos.relaxamento'))
    return redirect(url_for('dashboard'))

@conteudos_bp.route('/cadastrar/conteudo/<tipo>', methods=['POST'])
@login_required
def cadastrar_conteudo(tipo):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect('/')
    
    form = ConteudoForm()

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('dashboard'))

    titulo=form.titulo.data
    descricao=form.descricao.data
    assunto=form.assunto.data
    tipo_=tipo
    link=form.link.data
    
    novo_conteudo = Conteudo(titulo=titulo, descricao=descricao, assunto=assunto, tipo=tipo_, link=link)

    try:
        with get_session() as db:
            db.add(novo_conteudo)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))

    flash('Conteúdo adicionado com sucesso!', 'success')
    if tipo == 'material':
        return redirect(url_for('conteudos.conteudos'))
    elif tipo == 'relaxamento':
        return redirect(url_for('conteudos.relaxamento'))
    return redirect(url_for('dashboard'))


@conteudos_bp.route('/editar/conteudo/<int:conteudo_id>', methods=['POST'])
@login_required
def editar_conteudo(conteudo_id):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect('/')
    
    form = ConteudoForm()

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('dashboard'))

    try:
        with get_session() as db:
            conteudo = db.query(Conteudo).filter_by(id=conteudo_id).first()

            if not conteudo:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('dashboard'))

            conteudo.titulo = form.titulo.data
            conteudo.descricao = form.descricao.data
            conteudo.assunto = form.assunto.data
            conteudo.link = form.link.data

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))

    flash('Conteúdo editado com sucesso!', 'success')
    if conteudo.tipo == 'material':
        return redirect(url_for('conteudos.conteudos'))
    elif conteudo.tipo == 'relaxamento':
        return redirect(url_for('conteudos.relaxamento'))
    return redirect(url_for('dashboard'))


@conteudos_bp.route('/excluir/conteudo/<int:conteudo_id>', methods=['POST'])
@login_required
def excluir_conteudo(conteudo_id):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect('/')

    try:
        with get_session() as db:
            conteudo = db.query(Conteudo).filter_by(id=conteudo_id).first()
            if not conteudo:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('dashboard'))
            tipo = conteudo.tipo
            db.delete(conteudo)
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('dashboard'))

    flash('Conteúdo deletado com sucesso!', 'success')
    if tipo == 'material':
        return redirect(url_for('conteudos.conteudos'))
    elif tipo == 'relaxamento':
        return redirect(url_for('conteudos.relaxamento'))
    return redirect(url_for('dashboard'))