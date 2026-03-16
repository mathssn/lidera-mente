from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class EmocaoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    data_nascimento = DateField('Data de Nascimento', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('senha', 'Senhas diferentes')])
    submit = SubmitField("Enviar")



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Enviar")