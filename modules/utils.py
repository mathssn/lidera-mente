from flask import session, flash, redirect, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'nome' not in session or 'user_id' not in session:
            flash('Você precisa estar logado para acessar essa página', 'warning')
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated_function
