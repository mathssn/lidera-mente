from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, abort, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import resend
import glob

from database.models import Usuario
from database.db import get_session
from modules.usuario.forms import CadastroForm, LoginForm
from modules.utils import login_required

usuarios_bp = Blueprint('usuarios', __name__, template_folder='templates')
load_dotenv()
resend.api_key = os.environ.get('RESEND_API_KEY')

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


@usuarios_bp.route('/perfil')
@login_required
def perfil():
    try:
        with get_session() as db:
            usuario = db.query(Usuario).filter_by(id=session.get('user_id')).first()
            if not usuario:
                flash('Não é possivel acessar o perfil do usuário', 'warning')
                return redirect(url_for('logout'))
    except Exception as e:
        print(e)
        flash('Erro inesperado', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('perfil.html', usuario=usuario)


@usuarios_bp.route('/alterar-senha')
@login_required
def alterar_senha():
    pass



@usuarios_bp.route('/perfil-img')
@login_required
def perfil_img():
    pasta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'img-perfil')
    
    padrao = os.path.join(pasta, f"{session.get('user_id')}.*")
    arquivos = glob.glob(padrao)

    if not arquivos:
        abort(404)

    # Pega o primeiro arquivo encontrado
    caminho_arquivo = arquivos[0]
    nome_arquivo = os.path.basename(caminho_arquivo)

    return send_from_directory(pasta, nome_arquivo)


@usuarios_bp.route('/salvar-img', methods=['POST'])
@login_required
def salvar_img():
    file = request.files.get('foto')   

    if not file or file.filename == "":
        flash('Selecione um arquivo', 'warning')
        return jsonify({'sucesso': False})
    
    try:
        with get_session() as session_db:
            usuario = session_db.query(Usuario).filter_by(id=session.get('user_id')).first()
            if not usuario:
                flash('Não foi possivel identificar o usuário logado!', 'danger')
                return redirect(url_for('dashboard'))
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'img-perfil')
            os.makedirs(upload_path, exist_ok=True)

            files = os.listdir(upload_path)
            for f in files:
                name, ext = os.path.splitext(f)
                if name == str(usuario.id):
                    os.remove(os.path.join(upload_path, f))
            
            # O nome do arquivo será de acordo com o id da nota
            _, ext = os.path.splitext(file.filename)
            filepath = os.path.join(upload_path, str(usuario.id) + ext)
            file.save(filepath)
    except Exception as e:
        flash('Erro ao fazer upload da imagem!', 'danger')
        print(e)
        return jsonify({'sucesso': False})

    return jsonify({'sucesso': True})


@usuarios_bp.route('/remover-img', methods=['POST'])
@login_required
def remover_img():
    try:
        with get_session() as session_db:
            usuario = session_db.query(Usuario).filter_by(id=session.get('user_id')).first()
            if not usuario:
                flash('Não foi possivel identificar o usuário logado!', 'danger')
                return redirect(url_for('dashboard'))
            
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'img-perfil')
            files = os.listdir(upload_path)
            for f in files:
                name, ext = os.path.splitext(f)
                if name == str(usuario.id):
                    os.remove(os.path.join(upload_path, f))       
    except Exception as e:
        flash('Erro ao deletar a imagem!', 'danger')
        print(e)
        return jsonify({'sucesso': False})

    flash('Imagem removida!', 'success')
    return redirect(url_for('usuarios.perfil'))



@usuarios_bp.route('/editar/usuario', methods=['POST'])
@login_required
def editar_usuario():
    try:
        # Pegando dados do form
        nome = request.form.get('nome')
        email = request.form.get('email')
        data_nascimento = request.form.get('data_nascimento')

        with get_session() as db:
            usuario = db.query(Usuario).filter_by(id=session.get('user_id')).first()

            if not usuario:
                flash('Usuário não encontrado', 'warning')
                return redirect(url_for('usuarios.perfil'))
                    
            u = db.query(Usuario).filter_by(email=email).first()
            if u:
                flash('O email inserido já pertence a outro usuário', 'warning')
                return redirect(url_for('usuarios.perfil'))

            # Atualizando apenas se veio valor
            if nome:
                usuario.nome = nome
            if email:
                usuario.email = email
            if data_nascimento:
                usuario.data_nascimento = data_nascimento

            db.commit()


    except Exception as e:
        print(e)
        flash('Erro ao atualizar usuário', 'danger')
        return redirect(url_for('usuarios.perfil'))
    
    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('usuarios.perfil'))