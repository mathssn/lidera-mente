from flask import Blueprint, render_template, request, flash, redirect, url_for, session, current_app, abort, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from PIL import Image
import os
import resend
import io

from database.models import Usuario
from database.db import get_session
from modules.usuario.forms import CadastroForm, LoginForm, DesativarContaForm
from modules.utils import login_required

usuarios_bp = Blueprint('usuarios', __name__, template_folder='templates')
load_dotenv()
resend.api_key = os.environ.get('RESEND_API_KEY')


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3000):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except:
        return None
    
def generate_email_verification_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm')

def verify_email_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
    except Exception:
        return None
    return email


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
            session['email'] = user.email
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
    desativar_conta_form = DesativarContaForm()
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

    return render_template('perfil.html', usuario=usuario, desativar_conta_form=desativar_conta_form)



@usuarios_bp.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    try:
        # Pegando dados do form
        senha_atual = request.form.get('senha_atual')
        nova_senha = request.form.get('nova_senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if not senha_atual or not nova_senha or not confirmar_senha:
            flash('Preencha todos os campos', 'warning')
            return redirect(url_for('usuarios.perfil'))

        if nova_senha != confirmar_senha:
            flash('As novas senhas não coincidem', 'warning')
            return redirect(url_for('usuarios.perfil'))

        if len(nova_senha) < 8:
            flash('A sua senha deve conter 8 caracteres ou mais!', 'warning')
            return redirect(url_for('usuarios.perfil'))

        with get_session() as db:
            usuario = db.query(Usuario).filter_by(id=session.get('user_id')).first()

            if not usuario:
                flash('Usuário não encontrado', 'warning')
                return redirect(url_for('usuarios.perfil'))

            # Verifica se a senha atual está correta
            if not check_password_hash(usuario.senha, senha_atual):
                flash('Senha atual incorreta', 'danger')
                return redirect(url_for('usuarios.perfil'))

            if not usuario.email_confirmado:
                flash('Ação não permitida, faça a verificação do seu email primeiro!', 'warning')
                return redirect(url_for('usuarios.perfil'))

            # Atualiza a senha
            usuario.senha = generate_password_hash(nova_senha)
    except Exception as e:
        print(e)
        flash('Erro ao alterar senha', 'danger')
        return redirect(url_for('usuarios.perfil'))

    flash('Senha alterada com sucesso!', 'success')
    return redirect(url_for('usuarios.perfil'))


@usuarios_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email')
    if not email:
        flash('Insira um email!', 'danger')
        return redirect(url_for('usuarios.login'))
    
    try:
        with get_session() as db:
            user = db.query(Usuario).filter_by(email=email).first()
            if not user:
                flash('Email não encontrado, verifique e tente novamente!', 'danger')
                return redirect(url_for('usuarios.login'))

        token = generate_reset_token(email)
        reset_link = url_for('usuarios.reset_password', token=token, _external=True)

        email = resend.Emails.send({
            "from": "LideraMente <contato@lideramente.net>",
            "to": [email],
            "subject": "Alterar senha",
            "html": f'<p>Você está recebendo está mensagem pois foi feito um pedido para alterar a senha da sua conta.<br><br>Se não foi você que fez o pedido, ignore essa mensagem.<br><br>Link para alteração: {reset_link}</p>'
        })

        flash('O link para a alteração de sua senha foi mandado, cheque seu email', 'success')
    except Exception as e:
        flash('Erro ao enviar email! Tente novamente', 'danger')
        print(e)

    return redirect(url_for('usuarios.login'))


@usuarios_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Token invalido ou expirado!', 'danger')
        return redirect(url_for('usuarios.login'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('As senhas devem ser identicas', 'danger')
            return redirect(url_for('usuarios.reset_password', token=token))

        hash_password = generate_password_hash(new_password)

        try:
            with get_session() as db:
                user = db.query(Usuario).filter_by(email=email).first()
                if not user:
                    flash('Email não encontrado, verifique e tente novamente!', 'danger')
                    return redirect(url_for('usuarios.login'))
                
                user.senha = hash_password
                user.email_confirmado = True
                flash('Senha alterada com sucesso!', 'success')
                return redirect(url_for('usuarios.login'))
        except Exception as e:
            flash('Erro ao alterar senha!', 'danger')
            print(e)
            return redirect(url_for('usuarios.login')) 
    return render_template('reset_password.html', token=token)


@usuarios_bp.route('/perfil-img')
@login_required
def perfil_img():
    try:
        with get_session() as session_db:
            usuario = session_db.query(Usuario).filter_by(id=session.get('user_id')).first()

            if not usuario or not usuario.avatar:
                abort(404)

            return Response(usuario.avatar, mimetype=usuario.avatar_mimetype)
    except Exception as e:
        print(e)
        abort(404)


@usuarios_bp.route('/salvar-img', methods=['POST'])
@login_required
def salvar_img():
    file = request.files.get('foto')   

    if not file or file.filename == "":
        flash('Selecione um arquivo', 'warning')
        return jsonify({'sucesso': False})

    MAX_SIZE = 2 * 1024 * 1024  # 2MB
    file.seek(0, os.SEEK_END)
    tamanho = file.tell()
    file.seek(0)

    if tamanho > MAX_SIZE:
        flash('Imagem muito grande (máx: 2MB)', 'warning')
        return jsonify({'sucesso': False})

    try:
        image = Image.open(file)

        if image.format not in ['JPEG', 'JPG', 'PNG', 'WEBP']:
            flash('Formato inválido. Use JPG, PNG ou WEBP.', 'warning')
            return jsonify({'sucesso': False})

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail((300, 300))

        img_io = io.BytesIO()

        image.save(img_io, format='JPEG', quality=85, optimize=True)
        img_io.seek(0)

        with get_session() as session_db:
            usuario = session_db.query(Usuario).filter_by(id=session.get('user_id')).first()

            if not usuario:
                flash('Não foi possível identificar o usuário!', 'danger')
                return jsonify({'sucesso': False})

            usuario.avatar = img_io.read()
            usuario.avatar_mimetype = 'image/jpeg'  # padronizado

    except Exception as e:
        print(e)
        flash('Erro ao processar a imagem!', 'danger')
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
            
            usuario.avatar = None
            usuario.avatar_mimetype = None
    except Exception as e:
        flash('Erro ao deletar a imagem!', 'danger')
        print(e)
        return redirect(url_for('usuarios.perfil'))

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

            if email != usuario.email:    
                u = db.query(Usuario).filter_by(email=email).first()
                if u:
                    flash('O email inserido já pertence a outro usuário', 'warning')
                    return redirect(url_for('usuarios.perfil'))
            
            if not usuario.email_confirmado:
                flash('Faça a verificação do email para alteração de dados pessoais', 'warning')
                return redirect(url_for('usuarios.perfil'))

            # Atualizando apenas se veio valor
            if nome:
                usuario.nome = nome
            if email:
                usuario.email = email
            if data_nascimento:
                usuario.data_nascimento = data_nascimento
            nome = ''
            sobrenome = ''
            for i, letra in enumerate(usuario.nome):
                if letra == ' ':
                    sobrenome = usuario.nome[i:]
                    break
                nome += letra
            session['nome'] = nome
            session['sobrenome'] = sobrenome
    except Exception as e:
        print(e)
        flash('Erro ao atualizar usuário', 'danger')
        return redirect(url_for('usuarios.perfil'))
    
    flash('Usuário atualizado com sucesso!', 'success')
    return redirect(url_for('usuarios.perfil'))


@usuarios_bp.route('/desativar-conta', methods=['POST'])
@login_required
def desativar_conta():
    form = DesativarContaForm()
    if not form.validate_on_submit():
        flash('Insira dados válidos!', 'danger')
        return redirect(url_for('usuarios.perfil'))
    
    senha = form.senha.data

    try:
        with get_session() as db:
            user = db.query(Usuario).filter_by(id=session.get('user_id')).first()
            if not user:
                flash('Usuário não encontrado', 'warning')
                return redirect(url_for('usuarios.perfil'))
            
            if not check_password_hash(user.senha, senha):
                flash('Senha incorreta.', 'danger')
                return redirect(url_for('usuarios.perfil'))

            user.ativo = False
    except Exception as e:
        print(e)
        flash('Erro ao processar a desativação!', 'danger')
        return redirect(url_for('usuarios.perfil'))
    
    flash('Conta desativada com sucesso.', 'success')
    return redirect(url_for('usuarios.logout'))


@usuarios_bp.route('/send-verification-email', methods=['POST'])
@login_required
def send_verification_email():

    try:
        with get_session() as db:
            user = db.query(Usuario).filter_by(id=session.get('user_id')).first()
            if not user:
                flash('Usuário não encontrado!', 'danger')
                return redirect(url_for('usuarios.login'))
            
        token = generate_email_verification_token(user.email)
        verify_link = url_for('usuarios.verify_email', token=token, _external=True)

        resend.Emails.send({
            "from": "LideraMente <contato@lideramente.net>",
            "to": [user.email],
            "subject": "Verifique seu email",
            "html": f'''
                <p>Obrigado por se cadastrar!<br><br>
                Clique no link abaixo para verificar sua conta:<br><br>
                <a href="{verify_link}">Verificar Email</a><br><br>
                Se você não criou esta conta, ignore este email.</p>
            '''
        })

        flash('Email de verificação enviado!', 'success')
    except Exception as e:
        flash('Erro ao enviar email!1', 'danger')
        print(e)

    return redirect(url_for('usuarios.perfil'))


@usuarios_bp.route('/verify-email/<token>')
def verify_email(token):
    email = verify_email_verification_token(token)

    if not email:
        flash('Token inválido ou expirado!', 'danger')
        return redirect(url_for('usuarios.login'))

    try:
        with get_session() as db:
            user = db.query(Usuario).filter_by(email=email).first()

            if not user:
                flash('Usuário não encontrado!', 'danger')
                return redirect(url_for('usuarios.login'))

            if user.email_confirmado:
                flash('Email já foi verificado anteriormente!', 'info')
                return redirect(url_for('usuarios.login'))

            user.email_confirmado = True

        return render_template('email_verificado.html')

    except Exception as e:
        flash('Erro ao verificar email!', 'danger')
        print(e)
        return redirect(url_for('usuarios.login'))