from flask_mail import Mail, Message

from say.api.user_api import *
from say.api.need_api import *
from say.api.activity_api import *
from say.api.auth_api import *
from say.api.panel_auth_api import *
from say.api.dashboard_api import *
from say.api.family_api import *
from say.api.ngo_api import *
from say.api.privilege_api import *
from say.api.search_api import *
from say.api.social_worker_api import *
from say.api.child_api import *
from say.api.payment_api import *
from say.api.check_api import *
from say.api.invitation_api import *

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
