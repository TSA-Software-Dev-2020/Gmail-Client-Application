from flask_wtf import Form
from wtforms import TextField, PasswordField, IntegerField, BooleanField
from wtforms.fields import StringField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.


class RegisterForm(Form):
    name = TextField(
        'Username', validators=[DataRequired(), Length(min=6, max=25)]
    )
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=6, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )


class LoginForm(Form):
    agreed = BooleanField('Agree', [DataRequired()], default=False)


class ForgotForm(Form):
    email = TextField(
        'Email', validators=[DataRequired(), Length(min=6, max=40)]
    )

class ComposeForm(Form):
    recipient = TextField('Recipient', validators=[DataRequired(), Length(min=6, max=40)])
    subject = TextField('Subject', [DataRequired()])
    body = StringField('Message Body', [DataRequired()])

class TrashForm(Form):
    id = IntegerField('Message Id', validators=[DataRequired()])