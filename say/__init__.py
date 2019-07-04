from flask import Flask

from say.api.activity import activity
from say.api.privilege import privilege


app = Flask(__name__)
app.register_blueprint(api.activity.activity , url_prefix = '/api/v1')
app.register_blueprint(api.privilege.privilege , url_prefix = '/api/v1')
