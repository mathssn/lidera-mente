from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired


class EmocaoForm(FlaskForm):
    humor = SelectField(
        'Como está seu humor?', validators=[DataRequired()],
        choices=[
            ('feliz', '😃 Feliz'),
            ('triste', '😕 Triste'),
            ('entediado', '😐 Entediado'),
            ('raiva', '😡 Raiva')
        ]
    )
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    data_field = DateField('Data', validators=[DataRequired()])
    submit = SubmitField("Enviar")

