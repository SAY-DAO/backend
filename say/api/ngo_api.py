import traceback

from say.models.ngo_model import NgoModel
from say.models.social_worker_model import SocialWorkerModel
from . import *

"""
Activity APIs
"""

def sw_list(social_worker_list):
    res = {}
    for sw in social_worker_list:
        res[str(sw.id)] = obj_to_dict(sw)

    return res


class GetAllNgo(Resource):
    @swag_from("./docs/ngo/all.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngos = session.query(NgoModel).filter_by(isDeleted=False).all()

            fetch = {}
            for n in base_ngos:
                data = obj_to_dict(n)
                # if n.coordinatorId != 0:
                #     coordinator = (
                #         session.query(SocialWorkerModel.firstName, SocialWorkerModel.lastName)
                #         .filter_by(id=n.coordinatorId)
                #         .filter_by(isDeleted=False)
                #         .first()
                #     )
                
                # else:
                #     coordinator = ("سیده سارا", "موسوی")
                
                # data['coordinatorFirstName'] = coordinator[0]
                # data['coordinatorLastName'] = coordinator[1]
                # data['socialWorkers'] = sw_list(
                #     session.query(SocialWorkerModel)
                #     .filter_by(id_ngo=n.id)
                #     .filter_by(isDeleted=False)
                #     .all()
                # )
                fetch[str(n.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(make_response(jsonify({"msg": "sth is wrong!"}), 500))

        finally:
            session.close()
            return resp


class AddNgo(Resource):
    @swag_from("./docs/ngo/add.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            if len(session.query(NgoModel).all()):
                last_ngo = session.query(NgoModel).order_by(NgoModel.id.desc()).first()
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
                    os.mkdir(temp_logo_path)

                path = os.path.join(
                    temp_logo_path, str(current_id) + "-logo_" + filename
                )

                file.save(path)
                path = '/' + path

            logo_url = path
            country = int(request.form["country"])
            city = int(request.form["city"])
            coordinator_id = int(request.form["coordinatorId"])
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
            last_update_date = datetime.utcnow()

            new_ngo = NgoModel(
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
                lastUpdateDate=last_update_date,
                website=website,
            )

            session.add(new_ngo)
            session.commit()

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
    @swag_from("./docs/ngo/id.yml")
    def get(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(NgoModel)
                .filter_by(id=ngo_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if not base_ngo:
                resp = make_response(jsonify({"msg": "sth went wrong!"}), 500)
                session.close()
                return resp

            res = obj_to_dict(base_ngo)
            coordinator = (
                session.query(SocialWorkerModel.firstName, SocialWorkerModel.lastName)
                .filter_by(id=base_ngo.coordinatorId)
                .filter_by(isDeleted=False)
                .first()
            )
            
            res['coordinatorFirstName'] = coordinator[0]
            res['coordinatorLastName'] = coordinator[1]
            res['socialWorkers'] = sw_list(
                session.query(SocialWorkerModel)
                .filter_by(id_ngo=base_ngo.id)
                .filter_by(isDeleted=False)
                .all()
            )
            # rd = ', "registerDate": ' + str(res.pop('registerDate'))
            # lu = ', "lastUpdateDate": ' + str(res.pop('lastUpdateDate'))
            # out = str(eval(str(res).encode('utf-8'))).replace("'", '"').replace('}', rd + lu + '}')
            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(make_response(jsonify({"msg": "sth is wrong!"}), 500))

        finally:
            session.close()
            return resp


class GetNgoByCoordinatorId(Resource):
    @swag_from("./docs/ngo/coordinator.yml")
    def get(self, coordinator_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngos = (
                session.query(NgoModel)
                .filter_by(coordinatorId=coordinator_id)
                .filter_by(isDeleted=False)
                .all()
            )

            fetch = {}
            for n in base_ngos:
                if not n:
                    resp = make_response(jsonify({"msg": "sth went wrong!"}), 500)
                    session.close()
                    return resp

                data = obj_to_dict(n)
                coordinator = (
                    session.query(SocialWorkerModel.firstName, SocialWorkerModel.lastName)
                    .filter_by(id=n.coordinatorId)
                    .filter_by(isDeleted=False)
                    .first()
                )
                
                data['coordinatorFirstName'] = coordinator[0]
                data['coordinatorLastName'] = coordinator[1]
                data['socialWorkers'] = sw_list(
                    session.query(SocialWorkerModel)
                    .filter_by(id_ngo=n.id)
                    .filter_by(isDeleted=False)
                    .all()
                )
                fetch[str(n.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)

        finally:
            session.close()
            return resp


class GetNgoByName(Resource):
    @swag_from("./docs/ngo/name.yml")
    def get(self, name):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngos = (
                session.query(NgoModel)
                .filter_by(name=name)
                .filter_by(isDeleted=False)
                .all()
            )

            fetch = {}
            for n in base_ngos:
                if not n:
                    resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)
                    session.close()
                    return resp

                data = obj_to_dict(n)
                coordinator = (
                    session.query(SocialWorkerModel.firstName, SocialWorkerModel.lastName)
                    .filter_by(id=n.coordinatorId)
                    .filter_by(isDeleted=False)
                    .first()
                )
                
                data['coordinatorFirstName'] = coordinator[0]
                data['coordinatorLastName'] = coordinator[1]
                data['socialWorkers'] = sw_list(
                    session.query(SocialWorkerModel)
                    .filter_by(id_ngo=n.id)
                    .filter_by(isDeleted=False)
                    .all()
                )
                fetch[str(n.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)

        finally:
            session.close()
            return resp


class GetNgoByWebsite(Resource):
    @swag_from("./docs/ngo/website.yml")
    def get(self, website):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngos = (
                session.query(NgoModel)
                .filter_by(website=website)
                .filter_by(isDeleted=False)
                .all()
            )

            fetch = {}
            for n in base_ngos:
                if not n:
                    resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)
                    session.close()
                    return resp

                data = obj_to_dict(n)
                coordinator = (
                    session.query(SocialWorkerModel.firstName, SocialWorkerModel.lastName)
                    .filter_by(id=n.coordinatorId)
                    .filter_by(isDeleted=False)
                    .first()
                )
                
                data['coordinatorFirstName'] = coordinator[0]
                data['coordinatorLastName'] = coordinator[1]
                data['socialWorkers'] = sw_list(
                    session.query(SocialWorkerModel)
                    .filter_by(id_ngo=n.id)
                    .filter_by(isDeleted=False)
                    .all()
                )
                fetch[str(n.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)

        finally:
            session.close()
            return resp


class GetNgoByPhoneNumber(Resource):
    @swag_from("./docs/ngo/phone.yml")
    def get(self, phone_number):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngos = (
                session.query(NgoModel)
                .filter(NgoModel.phoneNumber.contains(phone_number))
                .filter_by(isDeleted=False)
                .all()
            )

            fetch = {}
            for n in base_ngos:
                if not n:
                    resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)
                    session.close()
                    return resp

                data = obj_to_dict(n)
                coordinator = (
                    session.query(SocialWorkerModel.firstName, SocialWorkerModel.lastName)
                    .filter_by(id=n.coordinatorId)
                    .filter_by(isDeleted=False)
                    .first()
                )
                
                data['coordinatorFirstName'] = coordinator[0]
                data['coordinatorLastName'] = coordinator[1]
                data['socialWorkers'] = sw_list(
                    session.query(SocialWorkerModel)
                    .filter_by(id_ngo=n.id)
                    .filter_by(isDeleted=False)
                    .all()
                )
                fetch[str(n.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)

        finally:
            session.close()
            return resp


class DeletePhoneNumber(Resource):
    @swag_from("./docs/ngo/delete_phone.yml")
    def patch(self, ngo_id, phone_number):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(NgoModel)
                .filter_by(id=ngo_id)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.phoneNumber = base_ngo.phoneNumber.replace(
                phone_number, ""
            ).replace(",,", ",")
            if base_ngo.phoneNumber[-1] == ",":
                base_ngo.phoneNumber = base_ngo.phoneNumber[:-1]

            session.commit()

            resp = make_response(jsonify(obj_to_dict(base_ngo)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"msg": "sth is wrong!"}), 500)

        finally:
            session.close()
            return resp


class UpdateNgo(Resource):
    @swag_from("./docs/ngo/update.yml")
    def patch(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(NgoModel)
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
                        os.mkdir(temp_logo_path)

                    for obj in os.listdir(temp_logo_path):
                        check = str(base_ngo.id) + "-logo"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_logo_path, obj))

                    base_ngo.logoUrl = os.path.join(
                        temp_logo_path, str(base_ngo.id) + "-logo_" + filename
                    )

                    file.save(base_ngo.logoUrl)
                    base_ngo.logoUrl = '/' + base_ngo.logoUrl

            base_ngo.lastUpdateDate = datetime.now()

            res = obj_to_dict(base_ngo)

            resp = make_response(jsonify(res), 200)
            session.commit()

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)
        finally:
            session.close()
            return resp


class DeleteNgo(Resource):
    @swag_from("./docs/ngo/delete.yml")
    def patch(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(NgoModel)
                .filter_by(id=ngo_id)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.isDeleted = True

            session.commit()

            resp = make_response(jsonify({"msg": "ngo deleted successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class DeactivateNgo(Resource):
    @swag_from("./docs/ngo/deactivate.yml")
    def patch(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(NgoModel)
                .filter_by(id=ngo_id)
                .filter_by(isActive=True)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.isActive = False

            session.commit()
            resp = make_response(jsonify({"msg": "ngo deactivated successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class ActivateNgo(Resource):
    @swag_from("./docs/ngo/activate.yml")
    def patch(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            base_ngo = (
                session.query(NgoModel)
                .filter_by(id=ngo_id)
                .filter_by(isActive=False)
                .filter_by(isDeleted=False)
                .first()
            )

            base_ngo.isActive = True

            session.commit()
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
api.add_resource(GetNgoByCoordinatorId, "/api/v2/ngo/coordinatorId=<coordinator_id>")
api.add_resource(GetNgoByName, "/api/v2/ngo/name=<name>")
api.add_resource(GetNgoByWebsite, "/api/v2/ngo/website=<website>")
api.add_resource(GetNgoByPhoneNumber, "/api/v2/ngo/phone=<phone_number>")
api.add_resource(DeletePhoneNumber, "/api/v2/ngo/ngoId=<ngo_id>&phone=<phone_number>")
api.add_resource(UpdateNgo, "/api/v2/ngo/update/ngoId=<ngo_id>")
api.add_resource(DeleteNgo, "/api/v2/ngo/delete/ngoId=<ngo_id>")
api.add_resource(DeactivateNgo, "/api/v2/ngo/deactivate/ngoId=<ngo_id>")
api.add_resource(ActivateNgo, "/api/v2/ngo/activate/ngoId=<ngo_id>")
