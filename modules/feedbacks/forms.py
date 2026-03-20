from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional


class FeedbackForm(FlaskForm):
    titulo = StringField('Titulo', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    evento_id = SelectField('Esse feedback se refere a algum evento?', coerce=lambda x: int(x) if x else None)
    data_field = DateField('Data(Deixe em branco p/ hoje)', validators=[Optional()])
    submit = SubmitField("Enviar")

