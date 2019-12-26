from collections import OrderedDict

from . import *
from say.api.need_api import get_need
from say.models.child_model import ChildModel
from say.models.child_need_model import ChildNeedModel
from say.models.family_model import FamilyModel
from say.models.need_family_model import NeedFamilyModel
from say.models.need_model import NeedModel
from say.models.ngo_model import NgoModel
from say.models.social_worker_model import SocialWorkerModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel


# api_bp = Blueprint('api', __name__)
# api = Api(api_bp)

"""
Child APIs
"""


def filter_by_confirm(child_query, confirm):
    confirm =  int(confirm)
    if confirm != 2:
        confirm = bool(confirm)
        return child_query.filter(ChildModel.isConfirmed==confirm)

    return child_query


def filter_by_privilege(query):  # TODO: priv
    user_role = get_user_role()
    sw_id = get_user_id()
    ngo_id = get_sw_ngo_id()

    if user_role in [SOCIAL_WORKER, COORDINATOR]:
        query = query \
            .filter_by(id_social_worker=sw_id)

    elif user_role in [NGO_SUPERVISOR]:
        query = query.filter_by(id_ngo=ngo_id)

    elif user_role in [USER]:
        query = filter_by_user(query)

    return query


def filter_by_user(query):  # TODO: priv
    user_id = get_user_id()

    query = query \
        .join(FamilyModel) \
        .join(UserFamilyModel) \
        .filter(UserFamilyModel.id_user==user_id) \
        .filter(UserFamilyModel.isDeleted==False) \

    return query


def filter_by_query(child_query):
    query = request.args

    ngo_id = query.get('ngo_id', None)
    sw_id = query.get('sw_id', None)
    sw_role = get_user_role()

    if sw_id:
        child_query = child_query \
            .filter_by(id_social_worker=sw_id)

    if ngo_id:
        child_query = child_query.filter_by(id_ngo=ngo_id)

    return child_query


def get_child_by_id(session, child_id, is_migrate=False, confirm=1, with_need=False):  # 2:all | 1:only confirmed | 0:only not confirmed
    if is_migrate:
        if int(confirm) == 0:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=False)
                .first()
            )
        elif int(confirm) == 1:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=True)
                .first()
            )
        elif int(confirm) == 2:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .first()
            )
        else:
            return {'message': 'wrong input'}
    else:
        if int(confirm) == 0:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=False)
                .filter_by(isMigrated=False)
                .first()
            )
        elif int(confirm) == 1:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=True)
                .filter_by(isMigrated=False)
                .first()
            )
        elif int(confirm) == 2:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .first()
            )
        else:
            return {'message': 'wrong input'}

    child_data = obj_to_dict(child)

    if with_need:
        child_data['Needs'] = get_child_need(session, child_id)

    child_data['ngoName'] = child.ngo.name
    child_data['socialWorkerFirstName'] = child.social_worker.firstName
    child_data['socialWorkerLastName'] = child.social_worker.lastName

    return child_data


def get_child_need(session, child_id, urgent=False, done=False,
                   with_participants=False, confirm=True):
    needs = session.query(NeedModel) \
        .filter_by(child_id=child_id) \
        .filter_by(isDeleted=False) \

    if confirm != 2:
        needs = needs.filter_by(isConfirmed=bool(confirm))

    child_needs, check = {}, False
    for need in needs:
        if done:
           if need.isDone:
                need_data = get_need(need, session, with_participants=with_participants, with_child_id=False)
                child_needs[str(need.id)] = need_data

        elif not urgent:
            need_data = get_need(need, session, with_participants=with_participants, with_child_id=False)
            child_needs[str(need.id)] = need_data

        else:
            if need.isUrgent:
                check = True
                need_data = get_need(need, session, with_participants=with_participants, with_child_id=False)
                child_needs[str(need.id)] = need_data

    if not check and urgent:
        return {'message': 'no urgent needs'}

    return child_needs


class GetAllChildren(Resource):

    def check_privileges(func):  # TODO: priv

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            query = request.args

            ngo_id = query.get('ngo_id', None)
            sw_id = query.get('sw_id', None)
            sw_role = get_user_role()

            if sw_role in [SOCIAL_WORKER, COORDINATOR]:
                if sw_id or ngo_id:
                    return HTTP_PERMISION_DENIED()

            if sw_role in [NGO_SUPERVISOR]:
                if ngo_id:
                    return HTTP_PERMISION_DENIED()

            return func(*args, **kwargs)

        return wrapper

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @check_privileges
    @swag_from("./docs/child/all.yml")
    def get(self, confirm):
        query = request.args.copy()
        take = query.get('take', 100)
        skip = query.get('skip', 0)
        ngo_id = query.get('ngo_id', None)
        sw_id = query.get('sw_id', None)

        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            confirm = int(confirm)
            children_query = (
                session.query(ChildModel)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
            )

            children_query = filter_by_privilege(children_query)
            children_query = filter_by_query(children_query)

            if int(confirm) == 0:
                children_query = children_query.filter_by(isConfirmed=False)
            elif int(confirm) == 1:
                children_query = children_query.filter_by(isConfirmed=True)

            children_query = children_query \
                .order_by(ChildModel.generatedCode.asc())

            children = children_query.offset(skip).limit(take)

            result = OrderedDict(
                totalCount=children_query.count(),
                children=[],
            )
            for child in children:
                result['children'].append(obj_to_dict(child))

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildById(Resource):

    @authorize(USER, SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/child/id.yml")
    def get(self, child_id, confirm):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child_id = int(child_id)
            child_query = session.query(ChildModel) \
                .filter(ChildModel.isDeleted==False) \
                .filter(ChildModel.isMigrated==False) \
                .filter(ChildModel.id==child_id)

            if child_id != DEFAULT_CHILD_ID:  # TODO: need needs
                child_query = filter_by_privilege(child_query)

            child_query = filter_by_confirm(child_query, confirm)

            child = child_query.one_or_none()
            if child is None:
                resp = HTTP_NOT_FOUND()
                return

            child_dict = obj_to_dict(child, relationships=True)
            if get_user_role() in [USER]:  # TODO: priv
                user_id = get_user_id()
                family_id = child.families[0].id
                child_family_member = []

                user_family = session.query(UserFamilyModel) \
                    .filter_by(isDeleted=False) \
                    .filter_by(id_user=user_id) \
                    .filter_by(id_family=family_id) \
                    .first()

                child_dict['familyId'] = family_id
                child_dict['userRole'] = user_family.userRole

                for member in child.families[0].current_members():
                    child_family_member.append(dict(
                        role=member.userRole,
                        firstName=member.user.firstName,
                        lastName=member.user.lastName,
                    ))

                child_dict["childFamilyMembers"] = child_family_member

                confirmed_needs = []
                for need in child_dict['needs']:
                    if not need['isConfirmed']:
                        continue
                    confirmed_needs.append(need)
                child_dict['needs'] = confirmed_needs

                del child_dict['social_worker']
                del child_dict['ngo']

            resp = make_response(jsonify(child_dict), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


# TODO: ngo_id is needed?
class AddChild(Resource):

    def check_privilege(self, sw_id, ngo_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id() or ngo_id != get_sw_ngo_id():
                return HTTP_PERMISION_DENIED()

        elif sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids or ngo_id != get_sw_ngo_id():
                return HTTP_PERMISION_DENIED()

        elif sw_role in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
            if sw_id not in allowed_sw_ids:
                return HTTP_PERMISION_DENIED()

        return None

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/child/add.yml")
    def post(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            ngo_id = int(request.form.get("ngo_id", get_sw_ngo_id()))
            sw_id = int(request.form.get("sw_id", get_user_id()))
            sw_role = get_user_role()

            allowed_sw_ids = []
            if sw_role in [NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
                allowed_sw_ids_tuple = session.query(SocialWorkerModel.id) \
                    .filter_by(isDeleted=False) \
                    .filter_by(id_ngo=ngo_id) \
                    .distinct() \
                    .all()

                allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

            error = self.check_privilege(sw_id, ngo_id, allowed_sw_ids)
            if error:
                resp = error
                return

            sw = session.query(SocialWorkerModel) \
                .filter_by(id=sw_id) \
                .filter_by(isDeleted=False) \
                .first()

            code = sw.generatedCode + format(sw.childCount + 1, "04d")

            avatar_path, slept_avatar_path, voice_path = \
                "wrong avatar", "wrong avatar", "wrong voice"

            if "nationality" in request.form.keys():
                nationality = int(request.form["nationality"])
            else:
                nationality = None

            if "housingStatus" in request.form.keys():
                housing_status = int(request.form["housingStatus"])
            else:
                housing_status = None

            if "firstName" in request.form.keys():
                first_name = request.form["firstName"]
            else:
                first_name = None

            if "lastName" in request.form.keys():
                last_name = request.form["lastName"]
            else:
                last_name = None

            if "birthPlace" in request.form.keys():
                birth_place = request.form["birthPlace"]
            else:
                birth_place = None

            if "birthDate" in request.form.keys():
                birth_date = datetime.strptime(request.form["birthDate"], "%Y-%m-%d")
            else:
                birth_date = None

            if "address" in request.form.keys():
                address = request.form["address"]
            else:
                address = None

            if "status" in request.form.keys():
                status = int(request.form["status"])
            else:
                status = None

            if "education" in request.form.keys():
                education = int(request.form["education"])
            else:
                education = None

            if "familyCount" in request.form.keys():
                family_count = int(request.form["familyCount"])
            else:
                family_count = None

            phone_number = request.form["phoneNumber"]
            bio = request.form["bio"]
            say_name = request.form["sayName"]
            country = int(request.form["country"])
            city = int(request.form["city"])
            bio_summary = request.form["bioSummary"]
            gender = True if request.form["gender"] == "true" else False

            avatar_url = avatar_path
            slept_avatar_url = slept_avatar_path
            voice_url = voice_path

            created_at = datetime.utcnow()
            last_update = datetime.utcnow()

            new_child = ChildModel(
                phoneNumber=phone_number,
                nationality=nationality,
                avatarUrl=avatar_url,
                sleptAvatarUrl=avatar_url,
                housingStatus=housing_status,
                firstName=first_name,
                lastName=last_name,
                familyCount=family_count,
                education=education,
                createdAt=created_at,
                birthPlace=birth_place,
                birthDate=birth_date,
                address=address,
                bio=bio,
                voiceUrl=voice_url,
                id_ngo=ngo_id,
                id_social_worker=sw_id,
                sayName=say_name,
                country=country,
                city=city,
                gender=gender,
                bioSummary=bio_summary,
                status=status,
                lastUpdate=last_update,
                generatedCode=code,
            )

            session.add(new_child)
            session.flush()

            if "voiceUrl" not in request.files or "avatarUrl" not in request.files:
                resp = make_response(jsonify({"message": "error occured in file uploading!"}), 500)
                session.close()
                return resp

            file1 = request.files["voiceUrl"]
            file2 = request.files["avatarUrl"]
            file3 = request.files["sleptAvatarUrl"]

            if file1.filename == "":
                resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY VOICE!"}), 500)

                session.close()
                return resp

            if file2.filename == "":
                resp = make_response(jsonify({"message": "error occurred --> empty avatar!"}), 500)

                session.close()
                return resp

            if file3.filename == "":
                resp = make_response(
                    jsonify(
                        {"message": "error occurred --> empty slept avatar!"}
                    ),
                    500,
                )

                session.close()
                return resp

            child_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                str(new_child.id) + "-child",
            )

            if not os.path.isdir(child_path):
                os.makedirs(child_path, exist_ok=True)

            need_path = os.path.join(child_path, "needs")
            if not os.path.isdir(need_path):
                os.makedirs(need_path, exist_ok=True)

            if file1 and allowed_voice(file1.filename):
                # filename1 = secure_filename(file1.filename)
                filename1 = code + "." + file1.filename.split(".")[-1]

                voice_path = os.path.join(
                    child_path,
                    str(new_child.id) + "-voice_" + filename1,
                )
                file1.save(voice_path)
                new_child.voiceUrl = '/' + voice_path

            if file2 and allowed_image(file2.filename):
                # filename2 = secure_filename(file2.filename)
                filename2 = code + "." + file2.filename.split(".")[-1]

                avatar_path = os.path.join(
                    child_path,
                    str(new_child.id) + "-avatar_" + filename2,
                )
                file2.save(avatar_path)
                new_child.avatarUrl = '/' + avatar_path

            if file3 and allowed_image(file3.filename):
                # filename3 = secure_filename(file3.filename)
                filename3 = code + "." + file3.filename.split(".")[-1]

                slept_avatar_path = os.path.join(
                    child_path,
                    str(new_child.id) + "-slept-avatar_" + filename3,
                )
                file3.save(slept_avatar_path)
                new_child.sleptAvatarUrl = '/' + slept_avatar_path


            new_child.ngo.childrenCount += 1
            new_child.social_worker.childCount += 1

            session.commit()

            resp = make_response(jsonify(obj_to_dict(new_child)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp



class UpdateChildById(Resource):

    def check_privilege(self, sw_id, ngo_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id() or ngo_id != get_sw_ngo_id():
                return HTTP_PERMISION_DENIED()

        elif sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids or ngo_id != get_sw_ngo_id():
                return HTTP_PERMISION_DENIED()

        return

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/child/update.yml")
    def patch(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)
        sw_role = get_user_role()

        try:
            primary_child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .first()
            )

            allowed_sw_ids = []
            if sw_role in [NGO_SUPERVISOR]:
                allowed_sw_ids_tuple = session.query(SocialWorkerModel.id) \
                    .filter_by(isDeleted=False) \
                    .filter_by(id_ngo=primary_child.id_ngo) \
                    .distinct() \
                    .all()

                allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

            error = self.check_privilege(
                primary_child.id_social_worker,
                primary_child.id_ngo,
                allowed_sw_ids,
            )

            if error:
                resp = error
                return

            if "avatarUrl" in request.files.keys():
                file2 = request.files["avatarUrl"]

                if file2.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY AVATAR!"}), 500)

                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    # filename2 = secure_filename(file2.filename)
                    filename2 = (
                        primary_child.generatedCode
                        + "."
                        + file2.filename.split(".")[-1]
                    )

                    temp_avatar_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(primary_child.id) + "-child"
                    )

                    for obj in os.listdir(temp_avatar_path):
                        check = str(primary_child.id) + "-avatar"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_avatar_path, obj))

                    primary_child.avatarUrl = os.path.join(
                        temp_avatar_path, str(primary_child.id) + "-avatar_" + filename2
                    )

                    file2.save(primary_child.avatarUrl)
                    primary_child.avatarUrl = '/' + primary_child.avatarUrl

            if "sleptAvatarUrl" in request.files.keys():
                file3 = request.files["sleptAvatarUrl"]

                if file3.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY SLEPT AVATAR!"}), 500)

                    session.close()
                    return resp

                if file3 and allowed_image(file3.filename):
                    # filename2 = secure_filename(file3.filename)
                    filename2 = (
                        primary_child.generatedCode
                        + "."
                        + file3.filename.split(".")[-1]
                    )

                    temp_sleptAvatar_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(primary_child.id) + "-child"
                    )

                    for obj in os.listdir(temp_sleptAvatar_path):
                        check = str(primary_child.id) + "-sleptAvatar"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_sleptAvatar_path, obj))

                    primary_child.sleptAvatarUrl = os.path.join(
                        temp_sleptAvatar_path, str(primary_child.id) + "-sleptAvatar_" + filename2
                    )

                    file3.save(primary_child.sleptAvatarUrl)
                    primary_child.sleptAvatarUrl = '/' + primary_child.sleptAvatarUrl

            if "voiceUrl" in request.files.keys():
                file1 = request.files["voiceUrl"]

                if file1.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY VOICE!"}), 500)

                    session.close()
                    return resp

                if file1 and allowed_voice(file1.filename):
                    # filename1 = secure_filename(file1.filename)
                    filename1 = (
                        primary_child.generatedCode
                        + "."
                        + file1.filename.split(".")[-1]
                    )

                    temp_voice_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(primary_child.id) + "-child"
                    )

                    for obj in os.listdir(temp_voice_path):
                        check = str(primary_child.id) + "-voice"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_voice_path, obj))

                    primary_child.voiceUrl = os.path.join(
                        temp_voice_path, str(primary_child.id) + "-voice_" + filename1
                    )

                    file1.save(primary_child.voiceUrl)
                    primary_child.voiceUrl = '/' + primary_child.voiceUrl

            if "phoneNumber" in request.form.keys():
                primary_child.phoneNumber = request.form["phoneNumber"]

            if "nationality" in request.form.keys():
                primary_child.nationality = int(request.form["nationality"])

            if "housingStatus" in request.form.keys():
                primary_child.housingStatus = int(request.form["housingStatus"])

            if "firstName" in request.form.keys():
                primary_child.firstName = request.form["firstName"]

            if "lastName" in request.form.keys():
                primary_child.lastName = request.form["lastName"]

            if "gender" in request.form.keys():
                primary_child.gender = (
                    True if request.form["gender"] == "true" else False
                )

            if "familyCount" in request.form.keys():
                primary_child.familyCount = int(request.form["familyCount"])

            if "country" in request.form.keys():
                primary_child.country = int(request.form["country"])

            if "city" in request.form.keys():
                primary_child.city = int(request.form["city"])

            if "status" in request.form.keys():
                primary_child.status = int(request.form["status"])

            if "education" in request.form.keys():
                primary_child.education = int(request.form["education"])

            if "birthPlace" in request.form.keys():
                primary_child.birthPlace = request.form["birthPlace"]

            if "birthDate" in request.form.keys():
                primary_child.birthDate = datetime.strptime(
                    request.form["birthDate"], "%Y-%m-%d"
                )

            if "address" in request.form.keys():
                primary_child.address = request.form["address"]

            if "bio" in request.form.keys():
                primary_child.bio = request.form["bio"]

            if "bioSummary" in request.form.keys():
                primary_child.bioSummary = request.form["bioSummary"]

            if "sayName" in request.form.keys():
                primary_child.sayName = request.form["sayName"]

            primary_child.lastUpdate = datetime.utcnow()

            # secondary_child = obj_to_dict(primary_child)
            secondary_child = get_child_by_id(session, primary_child.id, confirm=2)

            session.commit()

            resp = make_response(jsonify(secondary_child), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class DeleteChildById(Resource):

    def check_privilege(self, sw_id, ngo_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id() or ngo_id != get_sw_ngo_id():
                return HTTP_PERMISION_DENIED()

        if sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids or ngo_id != get_sw_ngo_id():
                return HTTP_PERMISION_DENIED()
        return

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/child/delete.yml")
    def patch(self, child_id):
        sw_role = get_user_role()

        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .first()
            )

            allowed_sw_ids = []
            if sw_role in [NGO_SUPERVISOR]:
                allowed_sw_ids_tuple = session.query(SocialWorkerModel.id) \
                    .filter_by(isDeleted=False) \
                    .filter_by(id_ngo=child.id_ngo) \
                    .distinct() \
                    .all()

                allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

            error = self.check_privilege(
                child.id_social_worker,
                child.id_ngo,
                allowed_sw_ids,
            )

            if error:
                resp = error
                return

            if not child.isConfirmed:
                family = (
                    session.query(FamilyModel)
                    .filter_by(isDeleted=False)
                    .filter_by(id_child=child_id)
                    .first()
                )
                needs = (
                    session.query(ChildNeedModel)
                    .filter_by(isDeleted=False)
                    .filter_by(id_child=child_id)
                )

                for need in needs:
                    need.isDeleted = True

                child.isDeleted = True

                if family:
                    family.isDeleted = True

                child.social_worker.currentChildCount -= 1
                child.ngo.currentChildrenCount -= 1

                session.commit()

                resp = make_response(jsonify({"message": "child deleted successfully!"}), 200)
            else:
                resp = make_response(jsonify({"message": "error: confirmed child cannot be deleted!"}), 500)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class ConfirmChild(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/child/confirm.yml")
    def patch(self, child_id):
        social_worker_id = get_user_id()

        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .first()
            )

            if child.migratedId is None:
                primary_child = child

                if primary_child.isConfirmed:
                    resp = make_response(jsonify({"message": "child has already been confirmed!"}), 500)
                    session.close()
                    return resp

                primary_child.isConfirmed = True
                primary_child.confirmUser = social_worker_id
                primary_child.confirmDate = datetime.utcnow()

                primary_child.ngo.currentChildrenCount += 1

                primary_child.social_worker.currentChildCount += 1

                new_family = FamilyModel(id_child=primary_child.id)

                session.add(new_family)
                session.commit()

            else:
                secondary_child = child

                if secondary_child.isConfirmed:
                    resp = make_response(jsonify({"message": "child has already been confirmed!"}), 500)
                    session.close()
                    return resp

                secondary_child.isConfirmed = True
                secondary_child.confirmUser = social_worker_id
                secondary_child.confirmDate = datetime.utcnow()

                primary_child = (
                    session.query(ChildModel)
                    .filter_by(id=secondary_child.migratedId)
                    .filter_by(isDeleted=False)
                    .first()
                )
                needs = (
                    session.query(ChildNeedModel)
                    .filter_by(id_child=secondary_child.migratedId)
                    .filter_by(isDeleted=False)
                    .all()
                )
                family = (
                    session.query(FamilyModel)
                    .filter_by(id_child=secondary_child.migratedId)
                    .filter_by(isDeleted=False)
                    .first()
                )

                if (
                    secondary_child.social_worker.ngo.id
                    != primary_child.id_ngo
                ):
                    previous_ngo = (
                        session.query(NgoModel)
                        .filter_by(id=primary_child.id_ngo)
                        .filter_by(isDeleted=False)
                        .first()
                    )

                    secondary_child.social_worker.ngo.childrenCount += 1
                    secondary_child.social_worker.ngo.currentChildrenCount += 1
                    previous_ngo.currentChildrenCount -= 1

                secondary_child.social_worker.childCount += 1
                secondary_child.social_worker.currentChildCount += 1
                secondary_child.social_worker.needCount += len(needs)
                secondary_child.social_worker.currentNeedCount += len(needs)

                primary_child.social_worker.currentChildCount -= 1
                primary_child.social_worker.currentNeedCount -= len(needs)

                family.id_child = secondary_child.id

                old_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], str(primary_child.id) + "-child"
                )
                new_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], str(secondary_child.id) + "-child"
                )

                shutil.copytree(old_path, new_path)
                shutil.rmtree(old_path)

                need_dump = {}
                for f in os.listdir(new_path):
                    if not os.path.isdir(os.path.join(new_path, f)):
                        if str(primary_child.id) + "-avatar_" in f:
                            avatar_new_path = os.path.join(
                                new_path,
                                str(secondary_child.id)
                                + "-voice_"
                                + secondary_child.generatedCode
                                + "."
                                + str(f.rsplit(".", 1)[1].lower()),
                            )
                            os.rename(os.path.join(new_path, f), avatar_new_path)
                            secondary_child.avatarUrl = avatar_new_path

                        if str(primary_child.id) + "-voice_" in f:
                            voice_new_path = os.path.join(
                                new_path,
                                str(secondary_child.id)
                                + "-voice_"
                                + secondary_child.generatedCode
                                + "."
                                + str(f.rsplit(".", 1)[1].lower()),
                            )
                            os.rename(os.path.join(new_path, f), voice_new_path)
                            secondary_child.voiceUrl = voice_new_path

                    else:
                        need_path = os.path.join(new_path, "needs")
                        for nf in os.listdir(need_path):
                            for n in os.listdir(os.path.join(need_path, nf)):
                                n.replace(
                                    str(primary_child.id) + "-child",
                                    str(secondary_child.id) + "-child",
                                )
                                temp_need_path = os.path.join(need_path, nf)
                                temp_need_path = os.path.join(temp_need_path, n)
                                need_dump[str(nf.split("-")[0])] = temp_need_path

                for need in needs:
                    need.id_child = secondary_child.id
                    need.need.imageUrl = need_dump[str(need.id_need)]

                session.commit()

            resp = make_response(jsonify({"message": "child confirmed successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


# TODO: Logical error, what happens to the family and needs
class MigrateChild(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/child/migrate.yml")
    def patch(self, child_id, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            if not child:
                resp = make_response(jsonify({"message": "child is already migrated or doesn't exist!"}), 500)
                session.close()
                return resp

            elif int(social_worker_id) == child.id_social_worker:
                resp = make_response(jsonify({"message": "child cannot be migrated to its current social worker!"}), 500)
                session.close()
                return resp

            social_worker = (
                session.query(SocialWorkerModel)
                .filter_by(id=social_worker_id)
                .filter_by(isDeleted=False)
                .first()
            )

            new_child = ChildModel(
                firstName=child.firstName,
                lastName=child.lastName,
                sayName=child.sayName,
                phoneNumber=child.phoneNumber,
                nationality=child.nationality,
                country=child.country,
                city=child.city,
                avatarUrl=child.avatarUrl,
                sleptAvatarUrl=child.sleptAvatarUrl,
                gender=child.gender,
                bio=child.bio,
                bioSummary=child.bioSummary,
                voiceUrl=child.voiceUrl,
                birthPlace=child.birthPlace,
                birthDate=child.birthDate,
                address=child.address,
                housingStatus=child.housingStatus,
                familyCount=child.familyCount,
                sayFamilyCount=child.sayFamilyCount,
                education=child.education,
                status=child.status,
                doneNeedCount=child.doneNeedCount,
                id_ngo=social_worker.id_ngo,
                id_social_worker=social_worker_id,
                spentCredit=child.spentCredit,
                createdAt=child.createdAt,
                lastUpdate=datetime.utcnow(),
                isConfirmed=False,
                generatedCode=social_worker.generatedCode
                + format(social_worker.childCount + 1, "04d"),
                isMigrated=False,
                migratedId=child.id,
                migrateDate=datetime.utcnow(),
            )

            child.isMigrated = True

            session.add(new_child)
            session.commit()

            resp = make_response(jsonify({"message": "child migrated successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetChildById, "/api/v2/child/childId=<child_id>&confirm=<confirm>")
api.add_resource(GetAllChildren, "/api/v2/child/all/confirm=<confirm>")
api.add_resource(
    AddChild,
    "/api/v2/child/add/",
)
api.add_resource(UpdateChildById, "/api/v2/child/update/childId=<child_id>")
api.add_resource(DeleteChildById, "/api/v2/child/delete/childId=<child_id>")
api.add_resource(
    ConfirmChild,
    "/api/v2/child/confirm/childId=<child_id>",
)
api.add_resource(
    MigrateChild,
    "/api/v2/child/migrate/childId=<child_id>&socialWorkerId=<social_worker_id>",
)
