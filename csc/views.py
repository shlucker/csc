import re

from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.view import view_config

from csc.models import User, Club, School, CompetitionHost, Company, Competition, Post
from .security import check_password


def _get_user(view):
    if view.username:
        return User.get_by_username(view.username)


class CscViews:
    def __init__(self, request):
        self.request = request
        self.username = request.authenticated_userid

    @view_config(route_name='club', renderer='templates/club.jinja2')
    def club(self):
        user = _get_user(self)
        club_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        club = Club.get_by_id(club_id)
        return {'name': 'User profile',
                'user': user,
                'club': club}

    @view_config(route_name='company', renderer='templates/company.jinja2')
    def company(self):
        user = _get_user(self)
        company_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        company = Company.get_by_id(company_id)
        return {'name': 'User profile',
                'user': user,
                'company': company}

    @view_config(route_name='competition', renderer='templates/competition.jinja2')
    def competition(self):
        user = _get_user(self)
        competition_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        competition = Competition.get_by_id(competition_id)
        return {'name': 'User profile',
                'user': user,
                'competition': competition}

    @view_config(route_name='competition_host', renderer='templates/competition_host.jinja2')
    def competition_host(self):
        user = _get_user(self)
        competition_host_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        competition_host = CompetitionHost.get_by_id(competition_host_id)
        return {'name': 'User profile',
                'user': user,
                'competition_host': competition_host}

    @view_config(route_name='create_user', renderer='templates/create_user.jinja2')
    def create_user(self):
        user = _get_user(self)
        if not user or not 'admin' in user:
            raise HTTPForbidden()
        return {'name': 'Create user',
                'user': user}

    @view_config(route_name='home', renderer='templates/home.jinja2')
    def home(self):
        user = _get_user(self)

        return {'name': 'Home',
                'user': user}

    @view_config(route_name='login', renderer='templates/login.jinja2')
    def login(self):
        request = self.request
        login_url = request.route_url('login')
        referrer = request.url
        if referrer.startswith(login_url):
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        username = request.params.get('username', '')
        password = request.params.get('password', '')
        if request.POST:
            user = User.get_by_username(username) if username else None
            if user and check_password(password, user['password']):
                headers = remember(request, username)
                return HTTPFound(location=came_from, headers=headers)
            message = 'Failed login'

        return {'name': 'Login',
                'message': message,
                'url': login_url,
                'came_from': came_from,
                'username': username}

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url, headers=headers)

    @view_config(route_name='register', renderer='templates/register.jinja2')
    def register(self):
        request = self.request

        username = request.params.get('username', '')
        email = request.params.get('email', '')
        password = request.params.get('password', '')
        confirm_password = request.params.get('confirm-password', '')

        errors = {}

        if request.POST:
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
                return HTTPFound(self.request.route_url('login', _query=(('username', username),)))

        return {'username': username,
                'email': email,
                'password': password,
                'errors': errors}

    @view_config(route_name='school', renderer='templates/school.jinja2')
    def school(self):
        user = _get_user(self)
        school_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        school = School.get_by_id(school_id)
        return {'name': 'User profile',
                'user': user,
                'school': school}

    @view_config(route_name='search', renderer='templates/search_result_small.jinja2')
    def search(self):
        txt = self.request.matchdict['txt']

        users = list(User.find_text(txt, 0, 5))
        posts = list(Post.find_text(txt, 0, 5))
        clubs = list(Club.find_text(txt, 0, 5))
        schools = list(School.find_text(txt, 0, 5))

        return {'users': users,
                'posts': posts,
                'clubs': clubs,
                'schools': schools}

    @view_config(route_name='user', renderer='templates/user.jinja2')
    def user(self):
        user = _get_user(self)

        user_profile_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))
        if not 'admin' in user and user._id != user_profile_id:
            raise HTTPForbidden()

        user_profile = User.get_by_id(user_profile_id)

        if not user_profile:
            raise HTTPNotFound()

        return {'name': 'User profile',
                'user': user,
                'user_profile': user_profile}


class TemporaryViews:
    def __init__(self, request):
        self.request = request
        self.username = request.authenticated_userid

    @view_config(route_name='test', renderer='templates/test.jinja2')
    def test(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test1', renderer='templates/test1.jinja2')
    def test1(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test2', renderer='templates/test2.jinja2')
    def test2(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test3', renderer='templates/test3.jinja2')
    def test3(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test4', renderer='templates/test4.jinja2')
    def test4(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test5', renderer='templates/test5.jinja2')
    def test5(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test6', renderer='templates/test6.jinja2')
    def test6(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test7', renderer='templates/test7.jinja2')
    def test7(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test8', renderer='templates/test8.jinja2')
    def test8(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test9', renderer='templates/test9.jinja2')
    def test9(self):
        user = _get_user(self)
        return {'user': user}

    @view_config(route_name='test10', renderer='templates/test10.jinja2')
    def test10(self):
        user = _get_user(self)
        return {'user': user}
