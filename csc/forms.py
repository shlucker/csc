import wtforms


class LoginForm(wtforms.Form):
    username = wtforms.StringField('Username', [wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Password', [wtforms.validators.DataRequired()])
    remember = wtforms.BooleanField('Remember me')
    came_from = wtforms.HiddenField('Came from')


class RegistrationForm(wtforms.Form):
    member_type = wtforms.SelectField('Member type',
                                      choices=[('user', 'Student'),
                                               ('cmpn', 'Company'),
                                               ('gest', 'Guest'),
                                               ('coho', 'Competition host')])
    username = wtforms.StringField('Username', [wtforms.validators.DataRequired()])
    email = wtforms.StringField('E-mail address', [wtforms.validators.DataRequired()])
    password = wtforms.PasswordField('Password', [
        wtforms.validators.DataRequired(),
        wtforms.validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = wtforms.PasswordField('Confirm password')
    accept_tos = wtforms.BooleanField('I accept the TOS', [wtforms.validators.DataRequired()])
