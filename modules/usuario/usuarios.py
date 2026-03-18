from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import Usuario
from database.db import get_session
from modules.usuario.forms import CadastroForm, LoginForm

usuarios_bp = Blueprint('usuarios', __name__, template_folder='templates')


@usuarios_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    if not form.validate_on_submit():
        flash('Insira dados válidos para o login!', 'danger')
        return redirect(url_for('usuarios.login'))

    email = form.email.data.strip()
    senha = form.senha.data.strip()

    try:
        with get_session() as db:
            user = db.query(Usuario).filter_by(email=email).first()
            if not user:
                flash('O email informado não está cadastrado!', 'warning')
                return redirect(url_for('usuarios.login'))
            if not check_password_hash(user.senha, senha):
                flash('Email ou senha incorretos! Tente novamente!', 'warning')
                return redirect(url_for('usuarios.login'))
            session['user_id'] = user.id
            nome = ''
            sobrenome = ''
            for i, letra in enumerate(user.nome):
                if letra == ' ':
                    sobrenome = user.nome[i:]
                    break
                nome += letra
            session['nome'] = nome
            session['sobrenome'] = sobrenome
    except Exception as e:
        print(e)
        flash('Erro inesperado!', 'danger')
        return redirect('/')

    flash('Usuário logado com sucesso!', 'success')
    return redirect(url_for('dashboard'))

@usuarios_bp.route('/logout')
def logout():
    session.pop('user_id')
    session.pop('nome')
    session.pop('sobrenome')
    return redirect('/')

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
    
    nome = form.nome.data.strip()
    email = form.email.data.strip()
    data_nascimento = form.data_nascimento.data
    senha = form.senha.data.strip()

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
        return redirect(url_for('usuarios.cadastro'))


    flash('Usuário cadastrado com sucesso', 'success')
    return redirect('/login')

