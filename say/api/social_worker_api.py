from hashlib import md5

from sqlalchemy.orm import joinedload

from say.models import session, obj_to_dict
from say.models import Child
from say.models.ngo_model import Ngo
from say.models.social_worker_model import SocialWorker
from say.models import commit
from . import *
from ..schema.social_worker import MigrateSocialWorkerChildrenSchema

"""
Social Worker APIs
"""


class GetAllSocialWorkers(Resource):

    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/all.yml")
    def get(self):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        try:
            social_workers = session.query(SocialWorker) \
                .filter_by(isDeleted=False)

            if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
                user_id = get_user_id()
                user = session.query(SocialWorker).get(user_id)
                social_workers = social_workers \
                    .filter_by(id_ngo=user.id_ngo)

            fetch = {}
            for social_worker in social_workers:
                data = obj_to_dict(social_worker)
                data['typeName'] = social_worker.privilege.name
                data['ngoName'] = social_worker.ngo.name
                fetch[str(social_worker.id)] = data

            resp = make_response(jsonify(fetch), 200)
            resp.headers["Access-Control-Allow-Origin"] = "*"

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class AddSocialWorker(Resource):
    panel_users = 0

    @authorize(SUPER_ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/add.yml")
    def post(self):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        try:
            if "country" in request.form.keys():
                country = int(request.form["country"])
            else:
                country = None

            if "city" in request.form.keys():
                city = int(request.form["city"])
            else:
                city = None

            if "firstName" in request.form.keys():
                first_name = request.form["firstName"]
            else:
                first_name = None

            if "birthCertificateNumber" in request.form.keys():
                birth_certificate_number = request.form[
                    "birthCertificateNumber"]
            else:
                birth_certificate_number = None

            if "passportNumber" in request.form.keys():
                passport_number = request.form["passportNumber"]
            else:
                passport_number = None

            if "postalAddress" in request.form.keys():
                postal_address = request.form["postalAddress"]
            else:
                postal_address = None

            if "bankAccountNumber" in request.form.keys():
                bank_account_number = request.form["bankAccountNumber"]
            else:
                bank_account_number = None

            if "bankAccountShebaNumber" in request.form.keys():
                bank_account_sheba_number = request.form[
                    "bankAccountShebaNumber"]
            else:
                bank_account_sheba_number = None

            if "bankAccountCardNumber" in request.form.keys():
                bank_account_card_number = request.form[
                    "bankAccountCardNumber"]
            else:
                bank_account_card_number = None

            if "birthDate" in request.form.keys():
                birth_date = datetime.strptime(request.form["birthDate"],
                                               "%Y-%m-%d")
            else:
                birth_date = None

            telegram_id = request.form["telegramId"]
            id_number = request.form["idNumber"]
            id_ngo = int(request.form["id_ngo"])
            id_type = int(request.form["id_type"])
            last_name = request.form["lastName"]
            gender = True if request.form["gender"] == "true" else False
            phone_number = request.form["phoneNumber"]
            emergency_phone_number = request.form["emergencyPhoneNumber"]
            email_address = request.form["emailAddress"]

            register_date = datetime.utcnow()
            last_login_date = datetime.utcnow()

            if id_ngo != 0:
                ngo = (session.query(Ngo).filter_by(
                    isDeleted=False).filter_by(id=id_ngo).first())
                generated_code = format(id_ngo, "03d") + format(
                    ngo.socialWorkerCount + 1, "03d")

                ngo.socialWorkerCount += 1
                ngo.currentSocialWorkerCount += 1

            else:
                self.panel_users += 1
                generated_code = format(id_ngo, "03d") + format(
                    self.panel_users, "03d")

            username = f'sw{generated_code}'

            new_social_worker = SocialWorker(
                id_ngo=id_ngo,
                country=country,
                city=city,
                id_type=id_type,
                firstName=first_name,
                lastName=last_name,
                userName=username,
                birthCertificateNumber=birth_certificate_number,
                idNumber=id_number,
                gender=gender,
                birthDate=birth_date,
                phoneNumber=phone_number,
                emergencyPhoneNumber=emergency_phone_number,
                emailAddress=email_address,
                telegramId=telegram_id,
                postalAddress=postal_address,
                bankAccountNumber=bank_account_number,
                bankAccountShebaNumber=bank_account_sheba_number,
                bankAccountCardNumber=bank_account_card_number,
                registerDate=register_date,
                lastLoginDate=last_login_date,
                passportNumber=passport_number,
                generatedCode=generated_code,
                password='',
                passportUrl='',
                avatarUrl='',
                idCardUrl='',
            )

            session.add(new_social_worker)
            session.flush()
            current_id = new_social_worker.id

            password = md5(("SayPanel" + str(current_id)).encode()).hexdigest()

            id_card, passport, avatar = (
                "wrong id card",
                "wrong passport",
                "wrong avatar",
            )
            if "avatarUrl" not in request.files:
                resp = make_response(
                    jsonify({"message": "ERROR OCCURRED IN FILE UPLOADING!"}),
                    500)
                session.close()
                return resp

            file3 = request.files["avatarUrl"]
            if file3.filename == "":
                resp = make_response(
                    jsonify({"message": "ERROR OCCURRED --> EMPTY AVATAR!"}),
                    500)
                session.close()
                return resp

            if file3 and allowed_image(file3.filename):
                # filename = secure_filename(file3.filename)
                filename3 = generated_code + "." + file3.filename.split(
                    ".")[-1]

                temp_avatar_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    str(current_id) + "-socialworker")

                if not os.path.isdir(temp_avatar_path):
                    os.makedirs(temp_avatar_path, exist_ok=True)

                avatar = os.path.join(temp_avatar_path,
                                      str(current_id) + "-avatar_" + filename3)

                file3.save(avatar)
                avatar = '/' + avatar

            if "idCardUrl" in request.files:
                file1 = request.files["idCardUrl"]

                if file1.filename == "":
                    resp = make_response(
                        jsonify(
                            {"message": "ERROR OCCURRED --> EMPTY ID CARD!"}),
                        500)
                    session.close()
                    return resp

                if file1 and allowed_image(file1.filename):
                    # filename = secure_filename(file1.filename)
                    filename1 = generated_code + "." + file1.filename.split(
                        ".")[-1]

                    temp_idcard_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        str(current_id) + "-socialworker")

                    if not os.path.isdir(temp_idcard_path):
                        os.makedirs(temp_idcard_path, exist_ok=True)

                    id_card = os.path.join(
                        temp_idcard_path,
                        str(current_id) + "-idcard_" + filename1)

                    file1.save(id_card)

                id_card_url = '/' +  id_card

            else:
                id_card_url = None

            if "passportUrl" in request.files:
                file2 = request.files["passportUrl"]

                if file2.filename == "":
                    resp = make_response(
                        jsonify(
                            {"message": "ERROR OCCURRED --> EMPTY PASSPORT!"}),
                        500)
                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    # filename = secure_filename(file2.filename)
                    filename2 = str(current_id) + "." + file2.filename.split(
                        ".")[-1]

                    temp_passport_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        str(current_id) + "-socialworker")

                    if not os.path.isdir(temp_passport_path):
                        os.makedirs(temp_passport_path, exist_ok=True)

                    passport = os.path.join(
                        temp_passport_path,
                        str(current_id) + "-passport_" + filename2)

                    file2.save(passport)

                passport_url = '/' + passport

            else:
                passport_url = None

            avatar_url = avatar

            new_social_worker.password = password,
            new_social_worker.passportUrl = passport_url,
            new_social_worker.avatarUrl = avatar_url,
            new_social_worker.idCardUrl = id_card_url,
            session.commit()

            resp = make_response(jsonify({"message": "social_worker is created"}),
                                 200)
            resp.headers["Access-Control-Allow-Origin"] = "*"

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)
        finally:
            session.close()
            return resp


class GetSocialWorkerById(Resource):

    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/id.yml")
    def get(self, social_worker_id):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        try:
            social_worker_query = session.query(SocialWorker) \
                .filter_by(id=social_worker_id) \
                .filter_by(isDeleted=False)

            if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
                user_id = get_user_id()
                user = session.query(SocialWorker).get(user_id)
                social_worker_query = social_worker_query \
                    .filter_by(id_ngo=user.id_ngo)

            social_worker = social_worker_query.first()

            if not social_worker:
                resp = make_response(jsonify({"message": "null error"}), 500)
                session.close()
                return resp

            res = obj_to_dict(social_worker)
            res['typeName'] = social_worker.privilege.name
            res['ngoName'] = social_worker.ngo.name if social_worker.id_ngo != 0 else 'SAY'
            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class GetSocialWorkerByNgoId(Resource):

    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/ngo.yml")
    def get(self, ngo_id):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        try:
            ngo_id = int(ngo_id)
            social_workers = session.query(SocialWorker) \
                .filter_by(id_ngo=ngo_id) \
                .filter_by(isDeleted=False)

            if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
                user_id = get_user_id()
                user = session.query(SocialWorker).get(user_id)
                if user.id_ngo != ngo_id:
                    resp = make_response(jsonify(
                        message='Permission Denied'),
                        403,
                    )
                    return

            fetch = {}
            for social_worker in social_workers:
                if not social_worker:
                    resp = make_response(jsonify({"message": "error"}), 500)
                    session.close()
                    return resp

                data = obj_to_dict(social_worker)
                data['typeName'] = social_worker.privilege.name
                data['ngoName'] = social_worker.ngo.name if social_worker.id_ngo != 0 else 'SAY'

                fetch[str(social_worker.id)] = data

            resp = make_response(jsonify(fetch), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class UpdateSocialWorker(Resource):

    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/update.yml")
    def patch(self, social_worker_id):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        ngo_change = False
        previous_ngo = None

        try:
            base_social_worker = session.query(SocialWorker) \
                .filter_by(id=social_worker_id) \
                .filter_by(isDeleted=False) \
                .first()

            if get_user_role() in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
                user_id = get_user_id()
                user = session.query(SocialWorker).get(user_id)
                if user.id_ngo != base_social_worker.id_ngo:
                    resp = make_response(
                        jsonify(message='Permission Denied'),
                        403,
                    )
                    return

            if "idCardUrl" in request.files.keys():
                file1 = request.files["idCardUrl"]

                if file1.filename == "":
                    resp = make_response(
                        jsonify({"message":
                                 "ERROR OCCURRED --> EMPTY VOICE!"}), 500)
                    session.close()
                    return resp

                if file1 and allowed_image(file1.filename):
                    # filename = secure_filename(file1.filename)
                    filename1 = (base_social_worker.generatedCode + "." +
                                 file1.filename.split(".")[-1])

                    temp_idcard_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        str(base_social_worker.id) + "-socialworker",
                    )

                    if not os.path.isdir(temp_idcard_path):
                        os.makedirs(temp_idcard_path, exist_ok=True)

                    for obj in os.listdir(temp_idcard_path):
                        check = str(base_social_worker.id) + "-idcard"
                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_idcard_path, obj))

                    base_social_worker.idCardUrl = os.path.join(
                        temp_idcard_path,
                        str(base_social_worker.id) + "-idcard_" + filename1,
                    )

                    file1.save(base_social_worker.idCardUrl)
                    base_social_worker.idCardUrl = \
                        '/' + base_social_worker.idCardUrl


            if "passportUrl" in request.files.keys():
                file2 = request.files["passportUrl"]

                if file2.filename == "":
                    resp = make_response(
                        jsonify({"message":
                                 "ERROR OCCURRED --> EMPTY VOICE!"}), 500)
                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    # filename = secure_filename(file1.filename)
                    filename2 = (base_social_worker.generatedCode + "." +
                                 file2.filename.split(".")[-1])

                    temp_passport_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        str(base_social_worker.id) + "-socialworker",
                    )

                    if not os.path.isdir(temp_passport_path):
                        os.makedirs(temp_passport_path, exist_ok=True)

                    for obj in os.listdir(temp_passport_path):
                        check = str(base_social_worker.id) + "-passport"
                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_passport_path, obj))

                    base_social_worker.passportUrl = os.path.join(
                        temp_passport_path,
                        str(base_social_worker.id) + "-passport_" + filename2,
                    )

                    file2.save(base_social_worker.passportUrl)

                    base_social_worker.passportUrl = '/' + base_social_worker.passportUrl

            if "avatarUrl" in request.files.keys():
                file3 = request.files["avatarUrl"]

                if file3.filename == "":
                    resp = make_response(
                        jsonify({"message":
                                 "ERROR OCCURRED --> EMPTY VOICE!"}), 500)
                    session.close()
                    return resp

                if file3 and allowed_image(file3.filename):
                    # filename = secure_filename(file1.filename)
                    filename3 = (base_social_worker.generatedCode + "." +
                                 file3.filename.split(".")[-1])

                    temp_avatar_path = os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        str(base_social_worker.id) + "-socialworker",
                    )

                    if not os.path.isdir(temp_avatar_path):
                        os.makedirs(temp_avatar_path, exist_ok=True)

                    for obj in os.listdir(temp_avatar_path):
                        check = str(base_social_worker.id) + "-avatar"
                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_avatar_path, obj))

                    base_social_worker.avatarUrl = os.path.join(
                        temp_avatar_path,
                        str(base_social_worker.id) + "-avatar_" + filename3,
                    )

                    file3.save(base_social_worker.avatarUrl)
                    base_social_worker.avatarUrl = \
                        '/' + base_social_worker.avatarUrl

            if "id_ngo" in request.form.keys():
                previous_ngo = base_social_worker.id_ngo
                base_social_worker.id_ngo = int(request.form["id_ngo"])
                ngo_change = True

            if "country" in request.form.keys():
                base_social_worker.country = int(request.form["country"])

            if "city" in request.form.keys():
                base_social_worker.city = int(request.form["city"])

            if "id_type" in request.form.keys():
                base_social_worker.id_type = int(request.form["id_type"])

            if "firstName" in request.form.keys():
                base_social_worker.firstName = request.form["firstName"]

            if "lastName" in request.form.keys():
                base_social_worker.lastName = request.form["lastName"]

            if "userName" in request.form.keys():
                base_social_worker.userName = request.form["userName"]

            if "birthCertificateNumber" in request.form.keys():
                base_social_worker.birthCertificateNumber = request.form[
                    "birthCertificateNumber"]

            if "idNumber" in request.form.keys():
                base_social_worker.idNumber = request.form["idNumber"]

            if "passportNumber" in request.form.keys():
                base_social_worker.passportNumber = request.form[
                    "passportNumber"]

            if "gender" in request.form.keys():
                base_social_worker.gender = (
                    True if request.form["gender"] == "true" else False)

            if "birthDate" in request.form.keys():
                base_social_worker.birthDate = datetime.strptime(
                    request.form["birthDate"], "%Y-%m-%d")

            if "phoneNumber" in request.form.keys():
                base_social_worker.phoneNumber = request.form["phoneNumber"]

            if "emergencyPhoneNumber" in request.form.keys():
                base_social_worker.emergencyPhoneNumber = request.form[
                    "emergencyPhoneNumber"]

            if "emailAddress" in request.form.keys():
                base_social_worker.emailAddress = request.form["emailAddress"]

            if "telegramId" in request.form.keys():
                base_social_worker.telegramId = request.form["telegramId"]

            if "postalAddress" in request.form.keys():
                base_social_worker.postalAddress = request.form[
                    "postalAddress"]

            if "bankAccountNumber" in request.form.keys():
                base_social_worker.bankAccountNumber = request.form[
                    "bankAccountNumber"]

            if "bankAccountShebaNumber" in request.form.keys():
                base_social_worker.bankAccountShebaNumber = request.form[
                    "bankAccountShebaNumber"]

            if "bankAccountCardNumber" in request.form.keys():
                base_social_worker.bankAccountCardNumber = request.form[
                    "bankAccountCardNumber"]

            if "password" in request.form.keys():
                base_social_worker.password = md5(
                    request.form["password"].encode()).hexdigest()


            res = obj_to_dict(base_social_worker)

            if ngo_change:
                that_ngo = (session.query(Ngo).filter_by(
                    id=previous_ngo).filter_by(isDeleted=False).first())
                this_ngo = (session.query(Ngo).filter_by(
                    id=base_social_worker.id_ngo).filter_by(
                        isDeleted=False).first())

                that_ngo.currentChildrenCount -= base_social_worker.currentChildCount
                that_ngo.currentSocialWorkerCount -= 1

                this_ngo.currentChildrenCount += base_social_worker.currentChildCount
                this_ngo.currentSocialWorkerCount += 1

                this_ngo.childrenCount += base_social_worker.childCount
                this_ngo.socialWorkerCount += 1

            session.add(base_social_worker)
            session.commit()
            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class DeleteSocialWorker(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/delete.yml")
    def patch(self, social_worker_id):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        try:
            base_social_worker = (session.query(SocialWorker).filter_by(
                id=social_worker_id).filter_by(isDeleted=False).first())

            base_social_worker.isDeleted = True
            this_ngo = session.query(Ngo) \
                .filter_by(id=base_social_worker.id_ngo) \
                .filter_by(isDeleted=False) \
                .first()

            this_ngo.currentChildrenCount -= base_social_worker.currentChildCount
            this_ngo.currentSocialWorkerCount -= 1

            session.commit()
            resp = make_response(
                jsonify({"message": "social worker deleted successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class DeactivateSocialWorker(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @commit
    @swag_from("./docs/social_worker/deactivate.yml")
    def patch(self, social_worker_id):

        sw = session.query(SocialWorker) \
            .filter_by(id=social_worker_id) \
            .filter_by(isDeleted=False) \
            .filter_by(isActive=True) \
            .with_for_update() \
            .one_or_none()

        if not sw:
            return {
                'message': f'Social worker {social_worker_id} not found',
            }, 404

        has_active_child = session.query(Child.id) \
            .filter(Child.id_social_worker==social_worker_id) \
            .filter(Child.isConfirmed.is_(True)) \
            .filter(Child.isDeleted.is_(False)) \
            .filter(Child.isMigrated.is_(False)) \
            .count()

        if has_active_child:
            return {
                'message': f'Social worker {social_worker_id} has active'
                    ' children and can not deactivate',
            }, 400

        sw.isActive = False
        return sw


class ActivateSocialWorker(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/social_worker/activate.yml")
    def patch(self, social_worker_id):
        resp = make_response(
            jsonify({"message": "major error occurred!"}),
            503,
        )

        try:
            base_social_worker = session.query(SocialWorker) \
                .filter_by(id=social_worker_id) \
                .filter_by(isDeleted=False) \
                .first()

            base_social_worker.isActive = True

            session.commit()
            resp = make_response(
                jsonify({"message": "social worker deactivated successfully!"}),
                200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "error"}), 500)

        finally:
            session.close()
            return resp


class MigrateSocialWorkerChildren(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @commit
    @swag_from("./docs/social_worker/migrate_children.yml")
    def post(self, id):
        try:
            data = MigrateSocialWorkerChildrenSchema(
                **request.form.to_dict(),
            )
        except ValueError as ex:
            return ex.json(), 400

        if data.destination_social_worker_id == id:
            return {'message': 'Can not migrate to same sw'}, 400

        sw = session.query(SocialWorker) \
            .filter_by(id=id) \
            .filter_by(isDeleted=False) \
            .filter_by(isActive=True) \
            .with_for_update(SocialWorker) \
            .one_or_none()

        if not sw:
            return {
                'message': f'Social worker {id} not found',
            }, 404

        destination_sw = session.query(SocialWorker) \
            .filter_by(id=data.destination_social_worker_id) \
            .filter_by(isDeleted=False) \
            .filter_by(isActive=True) \
            .with_for_update() \
            .one_or_none()

        if not destination_sw:
            return {
                'message': f'destination social worker not found',
            }, 400

        children = session.query(Child) \
            .filter(Child.id_social_worker == id) \
            .filter(Child.isDeleted.is_(False)) \
            .with_for_update()

        resp = []
        for child in children:
            migration = child.migrate(destination_sw)
            resp.append(migration)
        return resp


"""
API URLs
"""

api.add_resource(GetAllSocialWorkers, "/api/v2/socialWorker/all")
api.add_resource(AddSocialWorker, "/api/v2/socialWorker/add")
api.add_resource(
    GetSocialWorkerById,
    "/api/v2/socialWorker/socialWorkerId=<social_worker_id>",
)
api.add_resource(GetSocialWorkerByNgoId, "/api/v2/socialWorker/ngoId=<ngo_id>")
api.add_resource(
    UpdateSocialWorker,
    "/api/v2/socialWorker/update/socialWorkerId=<social_worker_id>",
)
api.add_resource(
    DeleteSocialWorker,
    "/api/v2/socialWorker/delete/socialWorkerId=<social_worker_id>",
)
api.add_resource(
    DeactivateSocialWorker,
    "/api/v2/socialWorker/deactivate/socialWorkerId=<social_worker_id>",
)
api.add_resource(
    ActivateSocialWorker,
    "/api/v2/socialWorker/activate/socialWorkerId=<social_worker_id>",
)

api.add_resource(
    MigrateSocialWorkerChildren,
    "/api/v2/socialWorker/<int:id>/children/migrate",
)
