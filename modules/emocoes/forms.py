from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, DateField, SubmitField, StringField
from wtforms.validators import DataRequired

class EmocaoForm(FlaskForm):
    humor = StringField('Qual é o humor?', validators=[DataRequired()])

    emoji = SelectField(
        'Escolha um emoji',
        validators=[DataRequired()],
        choices=[
            # felizes
            ('😀', '😀'),
            ('😃', '😃'),
            ('😄', '😄'),
            ('😁', '😁'),
            ('😊', '😊'),
            ('😎', '😎'),
            ('🥳', '🥳'),

            # neutros / meh
            ('😐', '😐'),
            ('😑', '😑'),
            ('😶', '😶'),

            # tristes
            ('😔', '😔'),
            ('😢', '😢'),
            ('😭', '😭'),
            ('☹️', '☹️'),

            # raiva / irritação
            ('😠', '😠'),
            ('😡', '😡'),
            ('🤬', '🤬'),

            # ansiedade / medo
            ('😰', '😰'),
            ('😨', '😨'),
            ('😟', '😟'),

            # cansaço
            ('😴', '😴'),
            ('🥱', '🥱'),

            # surpresa
            ('😲', '😲'),
            ('😮', '😮'),

            # amor / carinho
            ('😍', '😍'),
            ('🥰', '🥰'),
            ('❤️', '❤️'),

            # confusão
            ('🤔', '🤔'),
            ('😕', '😕')
        ]
    )

    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    data_field = DateField('Data', validators=[DataRequired()])
    submit = SubmitField("Enviar")