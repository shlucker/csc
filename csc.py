import cherrypy
import os
from models import User
from jinja2 import Environment, FileSystemLoader

import test
test.create()

env = Environment(loader=FileSystemLoader('templates'))

def render(template, params={}, headers={}):
    for header in headers:
        cherrypy.response.headers[header] = headers[header]
    tmpl = env.get_template(template)
    return tmpl.render(params)

class WebApp(object):

    @cherrypy.expose
    def index(self, user_name='', login=None):
        error_message = {}

        if login:
            try:
                user = User.get(name=user_name)
            except User.DoesNotExist as _e:
                error_message['user_name'] = 'User "{}" not found'.format(user_name)

            if not error_message:
                raise cherrypy.HTTPRedirect('user_profile?i={}'.format(user.id))

        return render('index.html',
                      params={'user_name': user_name,
                              'error_message': error_message})

    @cherrypy.expose
    def user_profile(self, i):
        user = User.get(id=i)
        return render('user_profile.html',
                      params={'user':user})


cherrypy.config.update({'log.access_file': 'access.log',
                        'log.error_file':  'error.log'})

path = os.path.abspath(os.path.dirname(__file__))
config = {'/img':          {'tools.staticdir.on':        True,
                            'tools.staticdir.dir':       path + '/img'},
          '/css':          {'tools.staticdir.on':        True,
                            'tools.staticdir.dir':       path + '/css'},
          '/js':           {'tools.staticdir.on':        True,
                            'tools.staticdir.dir':       path + '/js'},
          '/favicon.ico':  {'tools.staticfile.on':       True,
                            'tools.staticfile.filename': path + '/img/favicon.ico'}}

cherrypy.quickstart(WebApp(), '/', config)