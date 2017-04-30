# from pony.converting import str2date
from pony import orm
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.view import view_config

from csc.models import User, Notification, Club
from .security import check_password


class CscViews:
    @orm.db_session()
    def __init__(self, request):
        self.request = request
        self.user_id = request.authenticated_userid

    def _get_user(self):
        if self.user_id:
            return User.get(email=self.user_id)
        else:
            return None

    @view_config(route_name='create_user', renderer='templates/create_user.jinja2')
    @orm.db_session()
    def create_user(self):
        user = self._get_user()
        if not user or user.classtype != 'Administrator':
            raise HTTPForbidden()
        return {}

    @view_config(route_name='home')
    @orm.db_session()
    def home(self):
        user = self._get_user()

        notifications = notifications_from_clubs = user_clubs = []
        if user:
            notifications = user.to_notifications.select().order_by(orm.desc(Notification.date))
            if user.classtype == 'Member':
                user_clubs = user.clubs.select().order_by(Club.name)
                notifications_from_clubs = orm.select((n, c)
                                                      for n in Notification
                                                      for c in n.to_clubs
                                                      for u in c.members if u is user).order_by(
                    orm.desc(lambda n, c: n.date))

        return render_to_response('templates/home.jinja2',
                                  {'name': 'Home',
                                   'user': user,
                                   'user_clubs': user_clubs,
                                   'notifications': notifications,
                                   'notifications_from_clubs': notifications_from_clubs},
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
                user = User.get(email=email) if email else None
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
        user = self._get_user()
        user_profile_id = self.request.matchdict['user_id']

        if not user:
            return HTTPFound(self.request.route_url('login'))
        if user.classtype != 'Administrator' and user.id != int(user_profile_id):
            raise HTTPForbidden()

        user_profile = User[user_profile_id]
        return render_to_response('templates/user_profile.jinja2',
                                  {'name': 'User profile',
                                   'user': user,
                                   'user_profile': user_profile},
                                  request=self.request)
