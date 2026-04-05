from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Optional, Length, URL


class ConteudoForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional(), Length(max=400)])
    assunto = StringField('Assunto', validators=[Optional(), Length(max=100)])
    link = StringField('Link', validators=[Optional(), Length(max=400), URL(message='Insira uma URL válida')])
    submit = SubmitField("Salvar")
