import flask
import flask_login

app = flask.Flask(__name__)
app.secret_key = "super secret key"

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# import the definition of the views after defining all the global objects
import csc.views
