from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Nome Utente', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3)])
    remember_me = BooleanField('Ricordami')
    submit = SubmitField('Accedi al Sistema')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Password Attuale', validators=[
        DataRequired(message='Inserisci la password attuale'),
        Length(min=3, message='Password troppo corta')
    ])
    new_password = PasswordField('Nuova Password', validators=[
        DataRequired(message='Inserisci la nuova password'),
        Length(min=3, max=50, message='Password deve essere tra 3 e 50 caratteri')
    ])
    confirm_password = PasswordField('Conferma Nuova Password', validators=[
        DataRequired(message='Conferma la nuova password'),
        EqualTo('new_password', message='Le password non coincidono')
    ])
    submit = SubmitField('Cambia Password')
