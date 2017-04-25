# from pony.converting import str2date
import pony.orm as orm
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response
from pyramid.security import remember, forget
from pyramid.view import view_config, view_defaults

import csc.models as models
from .security import check_password


@view_defaults(renderer='templates/home.jinja2')
class CscViews:
    def __init__(self, request):
        with orm.db_session():
            self.request = request
            self.logged_in = request.authenticated_userid

    @view_config(route_name='home')
    def home(self):
        with orm.db_session():
            if self.logged_in:
                user = models.User.get(email=self.logged_in)
                # notifications = (n.post.title for n in user.to_notifications if n.date < str2date('2003-02-02'))
                # notifications = (n for n in user.to_notifications)
                notifications = orm.select(n for n in models.Notification if n in user.to_notifications).order_by(orm.desc(models.Notification.date))
            else:
                user = None
                notifications = []
            return render_to_response('templates/home.jinja2',
                                      {'name': 'Home', 'user': user, 'notifications': notifications},
                                      request=self.request)
            # return {'name': 'Home', 'user': user, 'notifications': notifications}

    @view_config(route_name='hello')
    def hello(self):
        return {'name': 'Hello View'}

    @view_config(route_name='login', renderer='templates/login.jinja2')
    def login(self):
        request = self.request
        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        email = ''
        password = ''
        if 'form.submitted' in request.POST:
            email = request.params['email']
            password = request.params['password']
            with orm.db_session():
                user = models.User.get(email=email)
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

    @view_config(route_name='user_profile', renderer='templates/user_profile.jinja2')
    def user_profile(self):
        return {}
