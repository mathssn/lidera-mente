from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SubmitField, HiddenField
from wtforms.validators import DataRequired, InputRequired


class EventoForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    data_hora = DateTimeField('Data e hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    cor = HiddenField('Cor', validators=[InputRequired()])
    submit = SubmitField("Salvar")

