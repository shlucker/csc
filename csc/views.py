import re
import uuid

import flask
import flask_bcrypt
import flask_login
import requests
import csc.exceptions

from csc import app
from csc.forms import RegistrationForm, LoginForm
from csc.models import User, Club, School, CompetitionHost, Company, Competition, Post, id2collection, MongoDbEntity, \
    LoggableUser
from csc.security import check_password


def _get_user():
    if flask_login.current_user:
        return User.get_by_username(flask_login.current_user)


########## Authentication ##########
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(flask.request.form)
    member = LoggableUser.get_by_username(form.username.data)

    if member is not None and flask_bcrypt.check_password_hash(member.password, form.password.data):
        flask_login.login_user(member, form.remember.data)

        if not member.email_verified:
            return flask.redirect(flask.url_for('verify_email', email=member.email))

        return flask.redirect(form.came_from.data or flask.url_for("home"))

    if flask.request.method == 'POST':
        flask.flash("<strong>Invalid Credentials.</strong> Please try again.", "danger")

    return flask.render_template('login.jinja2', form=form)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("home"))


@app.route('/recover')
def recover():
    return 'recover is not implemented yet'


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(flask.request.form)
    if flask.request.method == 'POST' and form.validate():
        member_type = form.member_type.data

        try:
            LoggableUser.create(username=form.username.data,
                                email=form.email.data,
                                password=form.password.data,
                                member_type=member_type)
        except csc.exceptions.DuplicatedEmail:
            flask.flash('The email address is already used')
            return flask.render_template('register.jinja2', form=form)
        except csc.exceptions.DuplicatedUserName:
            flask.flash('The username is already used')
            return flask.render_template('register.jinja2', form=form)

        return flask.redirect(flask.url_for('login', username=form.username.data))

    member_type = flask.request.args.get('member_type', None)
    if member_type:
        form.member_type.data = member_type

    return flask.render_template('register.jinja2', form=form)


@app.route('/register_preview')
def register_preview():
    return flask.render_template('register_preview.jinja2')


@app.route('/verify_email/<email>')
@app.route('/verify_email/<email>/<token>')
def verify_email(email, token=None):
    """
    token can be:
    - None      a page allowing to send the verification email is shown
    - 'send'    the email is sent and a page saying the verification email has been sent is shown
     - a uuid   the token is checked
    """
    member = LoggableUser.get_by_email(email)

    if not member:
        flask.flash('Email not found')
        flask.redirect('home')

    if member.email_verified:
        flask.flash('Email already verified')
        flask.redirect('login')

    if not token:
        return flask.render_template('verify_email.jinja2', email=email, token='send')

    if token == 'send':
        token = uuid.uuid4()
        member.set_field_value('verify_email_token', str(token))

        url = flask.url_for('verify_email', email=email, token=token, _external=True)
        subject = 'Member email verification'
        text = 'Please open a browser and navigate to the following url to verify the email address: ' + url
        html = 'Please click <a href="{}">here</a> to verify the email address'.format(url)
        recipients = [(member.name, email)]

        # TODO use uctechweb@gmail.com, or better setup the mail server and use donotreply@UCTechWeb.com
        ret = requests.post(
            "https://api.mailgun.net/v3/sandboxd6bc776b15c040088821fbdc2b437493.mailgun.org/messages",
            auth=("api", "key-62859cbba8f20f62ef18b35a3acdcd7d"),
            data={"from": "DoNotReply <donotreply@UCTechWeb.com>",
                  "to": recipients,
                  "subject": subject,
                  "text": text,
                  "html": html})
        assert ret.status_code == 200
        return flask.render_template('verify_email.jinja2', email=email, token='sent')

    if flask_login.current_user.verify_email_token == token:
        flask_login.current_user.set_email_verified()
        flask.flash('Email {} is verified'.format(email))
        return flask.redirect(flask.url_for('login'))

    flask.flash('The link used is not valid. Please send a new verification email.')
    return flask.render_template('verify_email.jinja2', email=email, token='send')


########## Views ##########
@app.route('/club/<id>')
def club(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))

    club = Club.get_by_id(id)
    return flask.render_template('club.jinja2', name='User profile', club=club)


@app.route('/company/<id>')
def company(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))

    company = Company.get_by_id(id)
    return flask.render_template('company.jinja2', name='User profile', company=company)


@app.route('/competition/<id>')
def competition(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))

    competition = Competition.get_by_id(id)
    return flask.render_template('competition.jinja2', name='User profile', competition=competition)


@app.route('/competition_host/<id>')
def competition_host(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))

    competition_host = CompetitionHost.get_by_id(id)
    return flask.render_template('competition_host.jinja2', name='User profile', competition_host=competition_host)


@app.route('/create_user')
def create_user():
    if not user or not 'admin' in user:
        raise flask.abort(403)
    return flask.render_template('create_user.jinja2', name='Create user')


@app.route('/entity/<id>')
def entity(id):
    """ Redirect to user, club or any other endpoint identified by id
    I don't like this function, this should never be called, but it works for now """
    prefix = id.split('-')[0]
    endpoint = id2collection[prefix].name
    return flask.redirect(flask.url_for(endpoint, id=id))


@app.route('/')
@app.route('/home')
def home():
    return flask.render_template('home.jinja2', name='Home')


@app.route('/school/<id>')
def school(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))

    school = School.get_by_id(id)
    return flask.render_template('school.jinja2', name='User profile', school=school)


@app.route('/search/<txt>' )
def search(txt):
    users = list(User.find_text(txt, 0, 5))
    posts = list(Post.find_text(txt, 0, 5))
    clubs = list(Club.find_text(txt, 0, 5))
    schools = list(School.find_text(txt, 0, 5))

    return flask.render_template('search_result_small.jinja2', users=users, posts=posts, clubs=clubs, schools=schools)

@app.route('/send_mass_message/', methods=['GET'])
@app.route('/send_mass_message/<id_to_add>', methods=['GET', 'POST'])
def send_mass_message(id_to_add=None):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))
    #if not 'admin' in flask_login.current_user and flask_login.current_user._id != id:
    #    raise flask.abort(403)

    if id_to_add is not None:
        new_user = User.get_by_id(id)
        new_club = Club.get_by_id(id)
    recipient_list = []
    users = []
    clubs = []

    #if not user_profile:
    #    raise flask.abort(404)

    return flask.render_template('mass_message_comp.jinja2', name='Send Mass Message', recipient_list=recipient_list,  users=users, clubs=clubs)


@app.route('/send_mass_message/append_search/<txt>')
def append_search(txt):
    users = list(User.find_text(txt, 0, 5))
    clubs = list(Club.find_text(txt, 0, 5))

    return flask.render_template('append_result_small.jinja2', users=users, clubs=clubs)


@app.route('/terms_and_conditions')
def terms_and_conditions():
    return flask.render_template('terms_and_conditions.jinja2')


@app.route('/user/<id>')
def user(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))
    if not 'admin' in flask_login.current_user and flask_login.current_user._id != id:
        raise flask.abort(403)

    user_profile = User.get_by_id(id)

    if not user_profile:
        raise flask.abort(404)

    return flask.render_template('user.jinja2', name='User profile', user_profile=user_profile)


########## TemporaryViews ##########
@app.route('/test')
def test():
    return flask.render_template('test.jinja2')


@app.route('/test1')
def test1():
    return flask.render_template('test1.jinja2')


@app.route('/test2')
def test2():
    return flask.render_template('test2.jinja2')


@app.route('/test3')
def test3():
    return flask.render_template('test3.jinja2')


@app.route('/test4')
def test4():
    return flask.render_template('test4.jinja2')


@app.route('/test5')
def test5():
    return flask.render_template('test5.jinja2')


@app.route('/test6')
def test6():
    return flask.render_template('test6.jinja2')


@app.route('/test7')
def test7():
    return flask.render_template('test7.jinja2')


@app.route('/test8')
def test8():
    return flask.render_template('test8.jinja2')


@app.route('/test9')
def test9():
    return flask.render_template('test9.jinja2')


@app.route('/test10')
def test10():
    return flask.render_template('test10.jinja2')
