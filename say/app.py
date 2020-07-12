import os
from logging import basicConfig, DEBUG

import flask_monitoringdashboard as dashboard
from flasgger import Swagger
from flask import (
    Flask,
)
from flask_caching import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flask_restful import Api
from mailerlite import MailerLiteApi

from say.celery import create_celery_app
from say.config import config
from say.payment import IDPay
from say.sms import MeliPayamak
from .orm import create_engine, init_model, session

PRODUCTION = os.environ.get('PRODUCTION')
DEFAULT_CHILD_ID = 104  # TODO: Remove this after implementing pre needs


basicConfig(level=DEBUG)


app = Flask(__name__)
app.config.update(config)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
celery = create_celery_app(app)
cache = Cache(app)
swagger = Swagger(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
)
mail = Mail(app)
jwt = JWTManager(app)
idpay = IDPay(app.config['IDPAY_API_KEY'], app.config['SANDBOX'])
sms_provider = MeliPayamak(
    app.config['MELI_PAYAMAK_USERNAME'],
    app.config['MELI_PAYAMAK_PASSWORD'],
    app.config['MELI_PAYAMAK_FROM'],
)
mailerlite = MailerLiteApi(app.config.get('MAILERLITE_API_KEY', 'not-entered'))

APIMD_CONFIG_FILE_PROD = 'apimd-config-prod.cfg'
APIMD_CONFIG_FILE = 'apimd-config.cfg'
if PRODUCTION:
    if not os.path.isfile(APIMD_CONFIG_FILE_PROD):
        raise Exception('''
            Make sure apimd-config-prod.cfg exist
            and admin PASSWORD, CUSTOM_LINK, SECURITY_TOKEN and DATABASE
            are correctly set in apimd-config-prod.cfg
        ''')

    dashboard.config.init_from(file=APIMD_CONFIG_FILE_PROD)
# else:
#     dashboard.config.init_from(file=APIMD_CONFIG_FILE)
#     print(
#         'Open http://localhost/dashboard and use admin admin to see '
#         'API monitoring dashboard'
#     )
#
# try:
#     dashboard.bind(app)
# except Exception as e:
#     print('''
#         Make sure apimd-config-prod.cfg exist
#         and admin PASSWORD, CUSTOM_LINK, SECURITY_TOKEN and DATABASE
#         are correctly set in apimd-config-prod.cfg
#         '''
#     )
#     raise

api = Api(app)

from .api import Login
api.add_resource(Login, "/api/v2/auth/login")
# api.add_resource(LogoutAccess, "/api/v2/auth/logout/token")
# api.add_resource(LogoutRefresh, "/api/v2/auth/logout/refresh")
# api.add_resource(TokenRefresh, "/api/v2/auth/refresh")
# api.add_resource(VerifyPhone, "/api/v2/auth/verify/phone")
# api.add_resource(VerifyEmail, "/api/v2/auth/verify/email")
# api.add_resource(ResetPasswordByEmailApi, "/api/v2/auth/password/reset/email")
# api.add_resource(ResetPasswordByPhoneApi, "/api/v2/auth/password/reset/phone")
# api.add_resource(
#     ConfirmResetPassword,
#     "/api/v2/auth/password/reset/confirm/token=<token>",
# )
# api.add_resource(GetActivityById, "/api/v2/activity/activityId=<activity_id>")
# api.add_resource(GetActivityBySocialWorker,
#                  "/api/v2/activity/socialWorker=<social_worker_id>")
# api.add_resource(GetActivityByType, "/api/v2/activity/type=<activity_code>")
# api.add_resource(GetAllActivities, "/api/v2/activity/all")
# api.add_resource(AddActivity,
#                  "/api/v2/activity/add/socialWorker=<social_worker_id>")
# api.add_resource(
#     ChangeCostAPi,
#     '/api/v2/need/<int:need_id>/change_cost',
# )
#
# api.add_resource(
#     ChangeCostRejectApi,
#     '/api/v2/need/<int:need_id>/change_cost/<id>/reject',
# )
#
# api.add_resource(
#     ChangeCostAcceptApi,
#     '/api/v2/need/<int:need_id>/change_cost/<id>/accept',
# )
#
# api.add_resource(
#     PendingChangeCostAPi,
#     '/api/v2/change_cost/pending',
# )
# api.add_resource(CheckUsername, '/api/v2/check/username/<username>')
# api.add_resource(CheckEmail, '/api/v2/check/email/<email>')
# api.add_resource(CheckPhone, '/api/v2/check/phone/<phone>')
#
# api.add_resource(GetActiveChildrenApi, "/api/v2/child/actives")
# api.add_resource(
#     GetChildById,
#     "/api/v2/child/childId=<child_id>&confirm=<confirm>",
# )
# api.add_resource(
#     GetChildByInvitationToken,
#     "/api/v2/child/invitations/<token>",
# )
# api.add_resource(GetChildNeeds, "/api/v2/child/childId=<child_id>/needs")
# api.add_resource(GetAllChildren, "/api/v2/child/all/confirm=<confirm>")
# api.add_resource(
#     AddChild,
#     "/api/v2/child/add/",
# )
# api.add_resource(UpdateChildById, "/api/v2/child/update/childId=<child_id>")
# api.add_resource(DeleteChildById, "/api/v2/child/delete/childId=<child_id>")
# api.add_resource(
#     ConfirmChild,
#     "/api/v2/child/confirm/childId=<child_id>",
# )
# api.add_resource(
#     MigrateChild,
#     "/api/v2/child/migrate/childId=<child_id>",
# )
# api.add_resource(
#     GoneChild,
#     "/api/v2/child/gone/childId=<child_id>&status=<new_status>",
# )
#
# api.add_resource(DashboardDataFeed, "/api/v2/dashboard")
# api.add_resource(GetFamilyById, "/api/v2/family/familyId=<family_id>")
# api.add_resource(
#     AddUserToFamily, "/api/v2/family/add"
# )
# api.add_resource(GetAllFamilies, "/api/v2/family/all")
# api.add_resource(
#     LeaveFamily,
#     "/api/v2/family/<family_id>/leave",
# )
#
# api.add_resource(InvitationAPI, "/api/v2/invitations/")
#
# api.add_resource(GetNeedById, "/api/v2/need/needId=<need_id>")
# api.add_resource(GetAllNeeds, "/api/v2/need/all/confirm=<confirm>")
# api.add_resource(UpdateNeedById, "/api/v2/need/update/needId=<need_id>")
# api.add_resource(DeleteNeedById, "/api/v2/need/delete/needId=<need_id>")
# api.add_resource(
#     ConfirmNeed,
#     "/api/v2/need/confirm/needId=<need_id>",
# )
# api.add_resource(AddNeed, "/api/v2/need/")
#
# api.add_resource(GetAllNgo, "/api/v2/ngo/all")
# api.add_resource(AddNgo, "/api/v2/ngo/add")
# api.add_resource(GetNgoById, "/api/v2/ngo/ngoId=<ngo_id>")
# api.add_resource(UpdateNgo, "/api/v2/ngo/update/ngoId=<ngo_id>")
# api.add_resource(DeleteNgo, "/api/v2/ngo/delete/ngoId=<ngo_id>")
# api.add_resource(DeactivateNgo, "/api/v2/ngo/deactivate/ngoId=<ngo_id>")
# api.add_resource(ActivateNgo, "/api/v2/ngo/activate/ngoId=<ngo_id>")
# api.add_resource(PanelLogin, "/api/v2/panel/auth/login")
#
# api.add_resource(PanelTokenRefresh, "/api/v2/panel/auth/refresh")
# api.add_resource(PanelLogoutAccess, "/api/v2/panel/auth/logout/token")
# api.add_resource(PanelLogoutRefresh, "/api/v2/panel/auth/logout/refresh")
# #api.add_resource(Logout, "/api/v2/panel/auth/logout/userid=<user_id>")
# #api.add_resource(Verify, "/api/v2/panel/auth/verify/userid=<user_id>")
# #api.add_resource(VerifyResend, "/api/v2/panel/auth/verify/resend/userid=<user_id>")
#
# api.add_resource(AddPayment, "/api/v2/payment")
# api.add_resource(GetPayment, "/api/v2/payment/<int:id>")
# api.add_resource(GetAllPayment, "/api/v2/payment/all")
# api.add_resource(VerifyPayment, "/api/v2/payment/verify")
#
# api.add_resource(GetAllPrivileges, "/api/v2/privilege/all")
# api.add_resource(AddPrivilege, "/api/v2/privilege/add")
# api.add_resource(GetPrivilegeByName, "/api/v2/privilege/name=<name>")
# api.add_resource(GetPrivilegeById, "/api/v2/privilege/privilegeId=<privilege_id>")
# api.add_resource(
#     GetPrivilegeByPrivilege, "/api/v2/privilege/privilege=<privilege_type>"
# )
# api.add_resource(UpdatePrivilege, "/api/v2/privilege/update/privilegeId=<privilege_id>")
#
# api.add_resource(GetRandomSearchResult,
#                  "/api/v2/search/random")
# api.add_resource(GetSayBrainSearchResult,
#                  "/api/v2/search/saybrain")
#
# api.add_resource(GetAllSocialWorkers, "/api/v2/socialWorker/all")
# api.add_resource(AddSocialWorker, "/api/v2/socialWorker/add")
# api.add_resource(
#     GetSocialWorkerById,
#     "/api/v2/socialWorker/socialWorkerId=<social_worker_id>",
# )
# api.add_resource(GetSocialWorkerByNgoId, "/api/v2/socialWorker/ngoId=<ngo_id>")
# api.add_resource(
#     UpdateSocialWorker,
#     "/api/v2/socialWorker/update/socialWorkerId=<social_worker_id>",
# )
# api.add_resource(
#     DeleteSocialWorker,
#     "/api/v2/socialWorker/delete/socialWorkerId=<social_worker_id>",
# )
# api.add_resource(
#     DeactivateSocialWorker,
#     "/api/v2/socialWorker/deactivate/socialWorkerId=<social_worker_id>",
# )
# api.add_resource(
#     ActivateSocialWorker,
#     "/api/v2/socialWorker/activate/socialWorkerId=<social_worker_id>",
# )
#
# api.add_resource(GetUserById, "/api/v2/user/userId=<user_id>")
# api.add_resource(GetUserChildren, "/api/v2/user/children/userId=<user_id>")
# api.add_resource(UpdateUserById, "/api/v2/user/update/userId=<user_id>")
# api.add_resource(DeleteUserById, "/api/v2/user/delete/userId=<user_id>")
# api.add_resource(AddUser, "/api/v2/user/add")
# api.add_resource(GetUserRole, "/api/v2/user/role/userId=<user_id>&childId=<child_id>")
#
#


@app.before_first_request
def init_orm():
    engine = create_engine(url=config['dbUrl'])
    init_model(engine)


@app.before_first_request
def create_data_dir():
    if not os.path.isdir(config['UPLOAD_FOLDER']):
        os.makedirs(config['UPLOAD_FOLDER'])


@app.teardown_request
def remove_session(ex):
    session.remove()


@app.teardown_appcontext
def dispose_engine(ex):
    session.bind.dispose()


# def insert_basedata():
#     try:
#         from say.basedata import basedata
#         basedata()
#     except:
#         pass
