import re

import flask
import flask_bcrypt
import flask_login

from csc import app
from csc.models import User, Club, School, CompetitionHost, Company, Competition, Post, id2collection
from csc.security import check_password


def _get_user():
    if flask_login.current_user:
        return User.get_by_username(flask_login.current_user)


########## Authentication ##########
@app.route('/login', methods=['GET', 'POST'])
def login():
    came_from = flask.request.form.get('came_from', None)
    username = flask.request.form.get('username', None)
    password = flask.request.form.get('password', None)
    remember = flask.request.form.get('remember', None)

    user = User.get_by_username(username)
    if user is not None and flask_bcrypt.check_password_hash(user.password, password):
        flask_login.login_user(user, remember)
        return flask.redirect(came_from or flask.url_for("home"))
    else:
        if flask.request.method == 'POST':
            flask.flash("<strong>Invalid Credentials.</strong> Please try again.", "danger")
        return flask.render_template('login.jinja2', name='Login', message='message', url='login_url',
                                     username=username, remember=remember, came_from=came_from)


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return flask.redirect(flask.url_for("home"))


@app.route('/recover')
def recover():
    return 'recover is not implemented yet'


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    username = flask.request.args.get('username', None)
    email = flask.request.args.get('email', None)
    password = flask.request.args.get('password', None)
    confirm_password = flask.request.args.get('confirm-password', None)

    errors = {}

    if flask.request.method == 'POST':
        if not username:
            errors['username'] = 'Missing username'
        else:
            if User.get_by_username(username):
                errors['username'] = 'Username not available'

        if not email:
            errors['email'] = 'Missing email'
        elif not re.match(r'\w+@\w+\.\w+', email):
            errors['email'] = 'Wrong email format'
        else:
            if User.get_by_email(email):
                errors['email'] = 'Email already used by another user'

        if not password:
            errors['password'] = 'Missing password'

        if password and not confirm_password:
            errors['confirm-password'] = 'Missing password'

        if password and confirm_password and password != confirm_password:
            errors['confirm-password'] = 'Passwords do not match'

        if not errors:
            User.create(username=username, email=email, password=password)
            return flask.redirect(flask.url_for('login', username=username))

    return flask.render_template('register.jinja2', username=username, email=email, password=password, errors=errors)


@app.route('/school/<id>')
def school(id):
    if not flask_login.current_user:
        return flask.redirect(flask.url_for('login'))

    school = School.get_by_id(id)
    return flask.render_template('school.jinja2', name='User profile', school=school)


@app.route('/search/<txt>')
def search(txt):
    users = list(User.find_text(txt, 0, 5))
    posts = list(Post.find_text(txt, 0, 5))
    clubs = list(Club.find_text(txt, 0, 5))
    schools = list(School.find_text(txt, 0, 5))

    return flask.render_template('search_result_small.jinja2', users=users, posts=posts, clubs=clubs, schools=schools)


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
