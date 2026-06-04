from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, URLField, SubmitField
from wtforms.validators import DataRequired, Optional, URL


class ContatoForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    link = URLField('Link', validators=[Optional(), URL()])
    submit = SubmitField('Enviar')


