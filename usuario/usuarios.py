from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import Usuario
from database.db import get_session
from usuario.forms import CadastroForm

usuarios_bp = Blueprint('usuarios', __name__, template_folder='templates')


@usuarios_bp.route('/login')
def login():
    return render_template('login.html')


@usuarios_bp.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    form = CadastroForm()
    if request.method == 'GET':
        return render_template('cadastro.html', form=form)
    if not form.validate_on_submit():
        print(form.errors.get('confirmar_senha'))
        if 'confirmar_senha' in form.errors and 'Senhas diferentes' in form.errors.get('confirmar_senha'):
            flash('As senhas devem ser identicas!', 'warning')
        else:
            flash('Insira dados válidos para o cadastro!', 'danger')
        return redirect(url_for('usuarios.cadastro'))
    
    nome = form.nome.data
    email = form.email.data
    data_nascimento = form.data_nascimento.data
    senha = form.senha.data
    confirmar_senha = form.confirmar_senha.data

    novo_usuario = Usuario(nome=nome, email=email, data_nascimento=data_nascimento, senha=generate_password_hash(senha))
    try:
        with get_session() as db:
            user = db.query(Usuario).filter_by(email=email).first()
            if user:
                flash('Esse Email já está cadastrado!', 'warning')
                return redirect(url_for('usuarios.cadastro'))
            db.add(novo_usuario)
    except Exception as e:
        print(e)
        flash('Erro inesperado', 'danger')
        return redirect('/')

    flash('Usuário cadastrado com sucesso', 'success')
    return redirect('/')

