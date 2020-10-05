import traceback

from say.models import session, obj_to_dict
from say.models.ngo_model import Ngo
from say.models.social_worker_model import SocialWorker
from . import *
from say.orm import safe_commit

"""
Activity APIs
"""

def sw_list(social_worker_list):
    res = {}
    for sw in social_worker_list:
        res[str(sw.id)] = obj_to_dict(sw)

    return res


class GetAllNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/all.yml")
    def get(self):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngos = session.query(Ngo).filter_by(isDeleted=False).all()

            fetch = {}
            for n in base_ngos:
                data = obj_to_dict(n)

                data['coordinator'] = obj_to_dict(n.coordinator)
                fetch[str(n.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(make_response(jsonify({"msg": "sth is wrong!"}), 500))

        finally:
            session.close()
            return resp


class AddNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/add.yml")
    def post(self):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            if len(session.query(Ngo).all()):
                last_ngo = session.query(Ngo).order_by(Ngo.id.desc()).first()
                current_id = last_ngo.id + 1
            else:
                current_id = 1

            path = "some wrong url"
            if "logoUrl" not in request.files:
                resp = make_response(jsonify({"message": "ERROR OCCURRED IN FILE UPLOADING!"}), 500)
                session.close()
                return resp

            file = request.files["logoUrl"]
            if file.filename == "":
                resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                session.close()
                return resp

            if file and allowed_image(file.filename):
                # filename = secure_filename(file.filename)
                filename = (
                    format(current_id, "03d") + "." + file.filename.split(".")[-1]
                )

                temp_logo_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], str(current_id) + "-ngo"
                )

                if not os.path.isdir(temp_logo_path):
                    os.makedirs(temp_logo_path, exist_ok=True)

                path = os.path.join(
                    temp_logo_path, str(current_id) + "-logo_" + filename
                )

                file.save(path)
                path = '/' + path

            logo_url = path
            country = int(request.form["country"])
            city = int(request.form["city"])
            try:
                coordinator_id = request.form.get("coordinatorId")
                if coordinator_id != None:
                    coordinator_id = int(coordinator_id)
            except (ValueError, TypeError):
                resp = make_response(
                    jsonify({"message": "invalid coordinatorId"}), 400,
                )
                return resp

            name = request.form["name"]
            postal_address = request.form["postalAddress"]
            email_address = request.form["emailAddress"]
            phone_number = request.form["phoneNumber"]
            if "balance" in request.form.keys():
                balance = request.form["balance"]
            else:
                balance = 0

            if "website" in request.form.keys():
                website = request.form["website"]
            else:
                website = None

            register_date = datetime.utcnow()

            new_ngo = Ngo(
                name=name,
                country=country,
                city=city,
                coordinatorId=coordinator_id,
                postalAddress=postal_address,
                emailAddress=email_address,
                phoneNumber=phone_number,
                logoUrl=logo_url,
                balance=balance,
                registerDate=register_date,
                website=website,
            )

            session.add(new_ngo)
            safe_commit(session)

            resp = make_response(jsonify({"msg": "ngo is created"}), 200)
            resp.headers["Access-Control-Allow-Origin"] = "*"

        except Exception as e:
            print(e)
            resp = make_response(
                jsonify({
                    "msg": "sth is wrong!",
                    "stack_trace": traceback.format_exc()
                }),
                500,
            )

        finally:
            session.close()
            return resp


class GetNgoById(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/id.yml")
    def get(self, ngo_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(Ngo)
                .filter_by(id=ngo_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if not base_ngo:
                resp = make_response(jsonify({"msg": "sth went wrong!"}), 500)
                session.close()
                return resp

            res = obj_to_dict(base_ngo)
            res['coordinatorFirstName'] = None
            res['coordinatorLastName'] = None

            if base_ngo.coordinatorId:
                coordinator = (
                    session.query(SocialWorker.firstName, SocialWorker.lastName)
                    .filter_by(id=base_ngo.coordinatorId)
                    .filter_by(isDeleted=False)
                    .first()
                )

                res['coordinatorFirstName'] = coordinator[0]
                res['coordinatorLastName'] = coordinator[1]

            res['socialWorkers'] = sw_list(
                session.query(SocialWorker)
                .filter_by(id_ngo=base_ngo.id)
                .filter_by(isDeleted=False)
                .all()
            )

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(make_response(jsonify({"msg": "sth is wrong!"}), 500))

        finally:
            session.close()
            return resp


class UpdateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/update.yml")
    def patch(self, ngo_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(Ngo)
                .filter_by(id=ngo_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if "country" in request.form.keys():
                base_ngo.country = int(request.form["country"])

            if "city" in request.form.keys():
                base_ngo.city = int(request.form["city"])

            if "coordinatorId" in request.form.keys():
                base_ngo.coordinatorId = int(request.form["coordinatorId"])

            if "name" in request.form.keys():
                base_ngo.name = request.form["name"]

            if "website" in request.form.keys():
                base_ngo.website = request.form["website"]

            if "postalAddress" in request.form.keys():
                base_ngo.postalAddress = request.form["postalAddress"]

            if "emailAddress" in request.form.keys():
                base_ngo.emailAddress = request.form["emailAddress"]

            if "phoneNumber" in request.form.keys():
                base_ngo.phoneNumber += "," + str(request.form["phoneNumber"])

            if "balance" in request.form.keys():
                base_ngo.balance = request.form["balance"]

            if "logoUrl" in request.files.keys():
                file = request.files["logoUrl"]

                if file.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                    session.close()
                    return resp

                if file and allowed_image(file.filename):
                    # filename = secure_filename(file.filename)
                    filename = (
                        format(base_ngo.id, "03d") + "." + file.filename.split(".")[-1]
                    )
                    temp_logo_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(base_ngo.id) + "-ngo"
                    )

                    if not os.path.isdir(temp_logo_path):
                        os.makedirs(temp_logo_path, exist_ok=True)

                    for obj in os.listdir(temp_logo_path):
                        check = str(base_ngo.id) + "-logo"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_logo_path, obj))

                    base_ngo.logoUrl = os.path.join(
                        temp_logo_path, str(base_ngo.id) + "-logo_" + filename
                    )

                    file.save(base_ngo.logoUrl)
                    base_ngo.logoUrl = '/' + base_ngo.logoUrl

            res = obj_to_dict(base_ngo)

            resp = make_response(jsonify(res), 200)
            safe_commit(session)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)
        finally:
            session.close()
            return resp


class DeleteNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/delete.yml")
    def patch(self, ngo_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(Ngo)
                .filter_by(id=ngo_id)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.isDeleted = True

            safe_commit(session)

            resp = make_response(jsonify({"msg": "ngo deleted successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class DeactivateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/deactivate.yml")
    def patch(self, ngo_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(Ngo)
                .filter_by(id=ngo_id)
                .filter_by(isActive=True)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.isActive = False

            safe_commit(session)
            resp = make_response(jsonify({"msg": "ngo deactivated successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class ActivateNgo(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/ngo/activate.yml")
    def patch(self, ngo_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(Ngo)
                .filter_by(id=ngo_id)
                .filter_by(isActive=False)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.isActive = True

            safe_commit(session)
            resp = make_response(jsonify({"msg": "ngo activated successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetAllNgo, "/api/v2/ngo/all")
api.add_resource(AddNgo, "/api/v2/ngo/add")
api.add_resource(GetNgoById, "/api/v2/ngo/ngoId=<ngo_id>")
api.add_resource(UpdateNgo, "/api/v2/ngo/update/ngoId=<ngo_id>")
api.add_resource(DeleteNgo, "/api/v2/ngo/delete/ngoId=<ngo_id>")
api.add_resource(DeactivateNgo, "/api/v2/ngo/deactivate/ngoId=<ngo_id>")
api.add_resource(ActivateNgo, "/api/v2/ngo/activate/ngoId=<ngo_id>")
