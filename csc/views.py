import re

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import remember, forget
from pyramid.view import view_config

from csc.models import User, Club, School, CompetitionHost, Company, Competition
from .security import check_password


class CscViews:
    def __init__(self, request):
        self.request = request
        self.username = request.authenticated_userid

    def _get_user(self):
        if self.username:
            return User.get_by_username(self.username)

    @view_config(route_name='club')
    def club(self):
        user = self._get_user()
        club_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        club = Club.get_by_id(club_id)
        return render_to_response('templates/club.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'club': club},
                                  request=self.request)

    @view_config(route_name='company')
    def company(self):
        user = self._get_user()
        company_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        company = Company.get_by_id(company_id)
        return render_to_response('templates/company.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'company': company},
                                  request=self.request)

    @view_config(route_name='competition')
    def competition(self):
        user = self._get_user()
        competition_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        competition = Competition.get_by_id(competition_id)
        return render_to_response('templates/competition.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'competition': competition},
                                  request=self.request)

    @view_config(route_name='competition_host')
    def competition_host(self):
        user = self._get_user()
        competition_host_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        competition_host = CompetitionHost.get_by_id(competition_host_id)
        return render_to_response('templates/competition_host.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'competition_host': competition_host},
                                  request=self.request)

    @view_config(route_name='create_user')
    def create_user(self):
        user = self._get_user()
        if not user or not 'admin' in user:
            raise HTTPForbidden()
        return render_to_response('templates/create_user.jinja2',
                                  {'name': 'Create user',
                                   'user': user},
                                  request=self.request)

    @view_config(route_name='home')
    def home(self):
        user = self._get_user()

        return render_to_response('templates/home.jinja2',
                                  {'name': 'Home',
                                   'user': user},
                                  request=self.request)

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

    @view_config(route_name='school')
    def school(self):
        user = self._get_user()
        school_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))

        school = School.get_by_id(school_id)
        return render_to_response('templates/school.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'school': school},
                                  request=self.request)

    @view_config(route_name='search')
    def search(self):
        user = self._get_user()
        txt = self.request.matchdict['txt']

        return Response('<li>Hi {}!</li>\n<li>Sorry, can\'t search for "{}" yet</li>'.format(user.name, txt))

    @view_config(route_name='test')
    def test(self):
        user = self._get_user()
        return render_to_response('templates/test.jinja2',
                                  {'user': user},
                                  request=self.request)

    @view_config(route_name='test1')
    def test1(self):
        user = self._get_user()
        return render_to_response('templates/test1.jinja2',
                                  {'user': user},
                                  request=self.request)

    @view_config(route_name='test2')
    def test2(self):
        user = self._get_user()
        return render_to_response('templates/test2.jinja2',
                                  {'user': user},
                                  request=self.request)

    @view_config(route_name='test3')
    def test3(self):
        user = self._get_user()
        return render_to_response('templates/test3.jinja2',
                                  {'user': user},
                                  request=self.request)

    @view_config(route_name='user')
    def user(self):
        user = self._get_user()
        user_profile_id = self.request.matchdict['id']

        if not user:
            return HTTPFound(self.request.route_url('login'))
        if not 'admin' in user and user._id != user_profile_id:
            raise HTTPForbidden()

        user_profile = User.get_by_id(user_profile_id)
        return render_to_response('templates/user.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'user_profile': user_profile},
                                  request=self.request)
