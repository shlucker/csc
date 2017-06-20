from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.view import view_config
from pyramid.response import Response

from csc.models import db, User, Club, School, CompetitionHost, Company, Competition
from .security import check_password


class CscViews:
    def __init__(self, request):
        self.request = request
        self.user_id = request.authenticated_userid

    def _get_user(self):
        if self.user_id:
            user = User.find_one({'email': self.user_id})
            if user:
                return User(user)

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
        if referrer == login_url:
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        email = request.params.get('email', '')
        password = request.params.get('password', '')
        if 'form.submitted' in request.POST:
            user = User.get_by_email(email) if email else None
            if user and check_password(password, user['password']):
                headers = remember(request, email)
                return HTTPFound(location=came_from, headers=headers)
            message = 'Failed login'

        return dict(
            name='Login',
            message=message,
            url=request.application_url + '/login',
            came_from=came_from,
            email=email,
        )

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url, headers=headers)

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
