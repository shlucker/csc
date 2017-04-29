# from pony.converting import str2date
import pony.orm as orm
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.view import view_config

import csc.models as models
from .security import check_password


class CscViews:
    @orm.db_session()
    def __init__(self, request):
        self.request = request
        self.user_id = request.authenticated_userid

    def _get_user(self):
        if self.user_id:
            self.user = models.User.get(email=self.user_id)
        else:
            self.user = None

    @view_config(route_name='create_user', renderer='templates/create_user.jinja2')
    @orm.db_session()
    def create_user(self):
        self._get_user()
        if not self.user or self.user.classtype != 'Administrator':
            raise HTTPForbidden()
        return {}

    @view_config(route_name='home')
    @orm.db_session()
    def home(self):
        self._get_user()
        if self.user:
            notifications = orm.select(n for n in models.Notification if n in self.user.to_notifications).order_by(
                orm.desc(models.Notification.date))
        else:
            notifications = []
        return render_to_response('templates/home.jinja2',
                                  {'name': 'Home',
                                   'user': self.user,
                                   'notifications': notifications},
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
            with orm.db_session():
                user = models.User.get(email=email) if email else None
            if user and check_password(password, user.password):
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

    @view_config(route_name='user_profile')
    @orm.db_session()
    def user_profile(self):
        self._get_user()
        user_profile_id = self.request.matchdict['user_id']

        if not self.user:
            return HTTPFound(self.request.route_url('login'))
        if self.user.classtype != 'Administrator' and self.user.id != int(user_profile_id):
            raise HTTPForbidden()

        user_profile = models.User[user_profile_id]
        return render_to_response('templates/user_profile.jinja2',
                                  {'name': 'User profile',
                                   'user': self.user,
                                   'user_profile': user_profile},
                                  request=self.request)
