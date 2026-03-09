from flask import Flask, render_template

from database.db import db, get_session
from database.models import Base
from database.insert import *

from usuario.usuarios import usuarios_bp

app = Flask(__name__)
app.secret_key = '1234'

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    Base.metadata.create_all(bind=db)
    app.register_blueprint(usuarios_bp)
    app.run(debug=True)