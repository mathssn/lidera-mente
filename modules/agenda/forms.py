from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SubmitField, SelectField
from wtforms.validators import DataRequired


class EventoForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição')
    data_hora = DateTimeField('Data e hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField("Salvar")


class TagForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    color = SelectField('Cor', validators=[DataRequired()],
        choices=[
            ('#32a852', 'Verde'),
            ('#ed0c0c', 'Vermelho')
        ]
    )
    submit = SubmitField("Salvar")