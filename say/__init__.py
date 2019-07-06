from flask import Flask

app = Flask(__name__)

from say.api.social_worker import socialworker
from say.api.ngo import ngo
from say.api.privilege import privilege
from say.api.activity import activity

app.register_blueprint(socialworker, url_prefix='/api/v1')
app.register_blueprint(ngo, url_prefix='/api/v1')
app.register_blueprint(privilege, url_prefix='/api/v1')
app.register_blueprint(activity, url_prefix='/api/v1')

# Middle Ware APIs

from say.api.authentication import authentication
from say.api.child import child
from say.api.need import need
from say.api.search import search




app.register_blueprint(authentication , url_prefix = '/api/v1')
app.register_blueprint(child , url_prefix = '/api/v1')
app.register_blueprint(need , url_prefix = '/api/v1')
app.register_blueprint(search , url_prefix = '/api/v1')
