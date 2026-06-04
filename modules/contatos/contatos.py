from flask import Blueprint, flash, redirect, render_template, url_for, request, session, abort, Response
from PIL import Image
import io

from modules.utils import login_required
from database.db import get_session
from database.models import Contato
from modules.contatos.forms import ContatoForm


contatos_bp = Blueprint(
    'contato',
    __name__,
    template_folder='templates'
)


@contatos_bp.route('/apoio')
@login_required
def apoio():
    form = ContatoForm()
    form_ed = ContatoForm()

    try:
        with get_session() as db:
            contatos_ = (
                db.query(Contato)
                .order_by(Contato.titulo)
                .all()
            )

    except Exception as e:
        print(e)
        contatos_ = []

    return render_template(
        'apoio.html',
        contatos=contatos_,
        form=form,
        form_ed=form_ed
    )


@contatos_bp.route('/cadastrar/contato', methods=['POST'])
@login_required
def cadastrar_contato():
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect(url_for('dashboard'))
    form = ContatoForm()

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('contato.apoio'))

    novo_contato = Contato(
        titulo=form.titulo.data,
        descricao=form.descricao.data,
        link=form.link.data
    )

    try:
        with get_session() as db:
            db.add(novo_contato)

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('contato.apoio'))

    flash('Contato adicionado com sucesso!', 'success')
    return redirect(url_for('contato.apoio'))


@contatos_bp.route('/editar/contato/<int:contato_id>', methods=['POST'])
@login_required
def editar_contato(contato_id):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect(url_for('dashboard'))
    form = ContatoForm()

    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('contato.apoio'))

    try:
        with get_session() as db:
            contato = db.query(Contato).filter_by(id=contato_id).first()

            if not contato:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('contato.apoio'))

            contato.titulo = form.titulo.data
            contato.descricao = form.descricao.data
            contato.link = form.link.data

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('contato.apoio'))

    flash('Contato editado com sucesso!', 'success')
    return redirect(url_for('contato.apoio'))


@contatos_bp.route('/excluir/contato/<int:contato_id>', methods=['POST'])
@login_required
def excluir_contato(contato_id):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect(url_for('dashboard'))
    try:
        with get_session() as db:
            contato = db.query(Contato).filter_by(id=contato_id).first()

            if not contato:
                flash('Registro não encontrado!', 'danger')
                return redirect(url_for('contato.apoio'))

            db.delete(contato)

    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect(url_for('contato.apoio'))

    flash('Contato deletado com sucesso!', 'success')
    return redirect(url_for('contato.apoio'))


@contatos_bp.route('/contato/imagem/<int:contato_id>')
def contato_carregar_imagem(contato_id):
    try:
        with get_session() as session_db:
            contato = session_db.query(Contato).filter_by(id=contato_id).first()

            if not contato or not contato.img:
                abort(404)

            return Response(contato.img, mimetype=contato.img_mimetype)
    except Exception as e:
        print(e)
        abort(404)

    return None


@contatos_bp.route('/contato/upload-imagem/<int:contato_id>', methods=['POST'])
@login_required
def contato_upload_imagem(contato_id):
    if session.get('email') != 'lidera.mente@gmail.com':
        return redirect(url_for('contato.apoio'))
    
    file = request.files.get('imagem')

    if not file or file.filename == "":
        flash('Selecione uma imagem', 'warning')
        return redirect(url_for('contato.apoio'))

    try:
        image = Image.open(file)

        if image.format not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
            flash('Formato inválido. Use JPG, PNG ou WEBP.', 'warning')
            return redirect(url_for('contato.apoio'))

        
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        img_io = io.BytesIO()

        image.save(img_io, format='JPEG', quality=100, optimize=True)
        img_io.seek(0)

        with get_session() as session_db:
            contato = session_db.query(Contato).filter_by(id=contato_id).first()

            if not contato:
                flash('Contato não encontrado!', 'danger')
                return redirect(url_for('contato.apoio'))

            contato.img = img_io.read()
            contato.img_mimetype = 'image/jpeg'

    except Exception as e:
        print(e)
        flash('Erro ao enviar imagem!', 'danger')
        return redirect(url_for('contato.apoio'))

    flash('Imagem alterada com sucesso!', 'success')
    return redirect(url_for('contato.apoio'))