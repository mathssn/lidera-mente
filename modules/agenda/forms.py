from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField
from wtforms.validators import DataRequired


class EventoForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = StringField('Descrição')
    data_hora = DateTimeField('Data e hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField("Salvar")


