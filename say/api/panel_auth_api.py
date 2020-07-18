from datetime import datetime
from hashlib import md5

from flask_jwt_extended import create_refresh_token, \
    jwt_refresh_token_required, get_jwt_identity, get_raw_jwt

from . import *
from say.models import session, obj_to_dict
from say.models.revoked_token_model import RevokedToken
from say.models.social_worker_model import SocialWorker


"""
Panel Authentication APIs
"""


class PanelLogin(Resource):

    @swag_from("./docs/panel_auth/login.yml")
    def post(self):
        resp = {"message": "Something is Wrong!"}

        try:
            if "username" in request.form.keys():
                username = request.form["username"]
            else:
                return make_response(
                    jsonify({"message": "username is needed!!!"}),
                    500,
                )

            if "password" in request.form.keys():
                password = md5(request.form["password"].encode()).hexdigest()
            else:
                return make_response(
                    jsonify({"message": "password is needed!!!"}),
                    500,
                )

            social_worker = (
                session.query(SocialWorker)
                .filter_by(isDeleted=False)
                .filter_by(isActive=True)
                .filter_by(userName=username)
                .first()
            )
            if social_worker is not None:
                if social_worker.password == password:
                    social_worker.lastLogin = datetime.utcnow()
                    session.commit()

                    access_token = create_sw_access_token(social_worker)

                    refresh_token = create_refresh_token(
                        identity = social_worker.id,
                    )

                    resp = jsonify({
                        "message": "Login Successful",
                        "access_token": f"Bearer {access_token}",
                        "refresh_token": f"Bearer {refresh_token}",
                    })
                else:
                    resp = make_response(
                        jsonify({"message": "UserName or Password is Wrong"}),
                        303,
                    )

            else:
                resp = make_response(
                    jsonify({"message": "Please Register First"}),
                    303,
                )

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


class PanelTokenRefresh(Resource):

    @jwt_refresh_token_required
    @swag_from("./docs/panel_auth/refresh.yml")
    def post(self):
        id = get_jwt_identity()
        social_worker = session.query(SocialWorker).get(id)
        session.close()
        access_token = create_sw_access_token(social_worker, fresh=True)
        return jsonify({'access_token': f'Bearer {access_token}'})


class PanelLogoutAccess(Resource):
    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/panel_auth/logout-access.yml")
    def post(self):
        jti = get_raw_jwt()['jti']
        msg = None
        try:
            revoked_token = RevokedToken(jti = jti)
            session.add(revoked_token)
            session.commit()
            msg = {'message': 'Access token has been revoked'}
        except:
            msg = {'message': 'Something went wrong'}, 500
        finally:
            session.close()
            return msg


class PanelLogoutRefresh(Resource):
    @jwt_refresh_token_required
    @swag_from("./docs/panel_auth/logout-refresh.yml")
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            session.add(revoked_token)
            session.commit()
            msg = {'message': 'Refresh token has been revoked'}
        except:
            msg = {'message': 'Something went wrong'}, 500
        finally:
            session.close()
            return msg

"""
API URLs
"""


api.add_resource(PanelLogin, "/api/v2/panel/auth/login")
api.add_resource(PanelTokenRefresh, "/api/v2/panel/auth/refresh")
api.add_resource(PanelLogoutAccess, "/api/v2/panel/auth/logout/token")
api.add_resource(PanelLogoutRefresh, "/api/v2/panel/auth/logout/refresh")
#api.add_resource(Logout, "/api/v2/panel/auth/logout/userid=<user_id>")
#api.add_resource(Verify, "/api/v2/panel/auth/verify/userid=<user_id>")
#api.add_resource(VerifyResend, "/api/v2/panel/auth/verify/resend/userid=<user_id>")
