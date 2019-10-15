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
from . import *

# api_bp = Blueprint('api', __name__)
# api = Api(api_bp)

"""
Child APis
"""


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

    return child_data


def get_child_need(session, child_id, urgent=False, done=False, with_participants=False):
    need_ids = session.query(ChildNeedModel).filter_by(id_child=child_id).filter_by(isDeleted=False).all()
    ids = [n.id_need for n in need_ids]
    needs = session.query(NeedModel).filter(NeedModel.id.in_(ids)).filter_by(isDeleted=False).all()

    child_needs, check = {}, False
    for need in needs:
        if not need.isConfirmed:
            continue

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
    @swag_from("./docs/child/all.yml")
    def get(self, confirm):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            confirm = int(confirm)
            children_query = (
                session.query(ChildModel)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
            )

            if int(confirm) == 0:
                children_query = children_query.filter_by(isConfirmed=False)
            elif int(confirm) == 1:
                children_query = children_query.filter_by(isConfirmed=True)

            children = children_query.all()
            if len(children) == 0:
                resp = make_response(jsonify({}), 200)

            result = {}
            for child in children:
                result[str(child.id)] = get_child_by_id(session,
                                                        child.id,
                                                        confirm=confirm,
                                                        with_need=True)

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildById(Resource):
    @swag_from("./docs/child/id.yml")
    def get(self, child_id, confirm):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_child_by_id(session, child_id, confirm=confirm, with_need=True)), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildrenOfUserByUserId(Resource):
    @swag_from("./docs/child/user_children.yml")
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            users = (
                session.query(UserFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(isDeleted=False)
                .all()
            )

            child_res = {}
            for user in users:
                families = (
                    session.query(FamilyModel)
                    .filter_by(id=user.id_family)
                    .filter_by(isDeleted=False)
                    .all()
                )

                for family in families:
                    child_data = get_child_by_id(
                        session, family.family_child_relation.id
                    )
                    child_res[str(family.id_child)] = child_data

            resp = make_response(jsonify(child_res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildNeeds(Resource):
    @swag_from("./docs/child/needs.yml")
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_child_need(session, child_id, with_participants=True)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildDoneNeeds(Resource):
    @swag_from("./docs/child/done.yml")
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_child_need(session, child_id, done=True)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildNeedsByCategory(Resource):
    @swag_from("./docs/child/category.yml")
    def get(self, child_id, category):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            needs = (
                session.query(ChildNeedModel)
                .filter_by(isDeleted=False)
                .filter_by(id_child=child_id)
                .all()
            )

            res = {}
            for need in needs:
                if need.need_relation.category == int(category):
                    need_data = (
                        session.query(NeedModel)
                        .filter_by(id=need.id_need)
                        .filter_by(isDeleted=False)
                        .filter_by(isConfirmed=True)
                        .first()
                    )
                    res[str(need.id_need)] = get_need(need_data, session)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildSayName(Resource):
    @swag_from("./docs/child/say_name.yml")
    def get(self, child_id):
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

            resp = make_response(jsonify({"ChildSayName": child.sayName}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildFamilyId(Resource):
    @swag_from("./docs/child/family_id.yml")
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            family = (
                session.query(FamilyModel)
                .filter_by(id_child=child_id)
                .filter_by(isDeleted=False)
                .first()
            )

            resp = make_response(jsonify({"ChildFamilyId": family.id}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildAvatarUrl(Resource):
    @swag_from("./docs/child/avatar.yml")
    def get(self, child_id):
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

            resp = make_response(jsonify({"ChildAvatarUrl": child.avatarUrl}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildCreditSpent(Resource):
    @swag_from("./docs/child/spent.yml")
    def get(self, child_id):
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

            resp = make_response(jsonify({"ChildCreditSpent": child.spentCredit}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddChild(Resource):
    @swag_from("./docs/child/add.yml")
    def post(self, social_worker_id, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            sw = (
                session.query(SocialWorkerModel)
                .filter_by(id=social_worker_id)
                .filter_by(isDeleted=False)
                .first()
            )

            code = sw.generatedCode + format(sw.childCount + 1, "04d")

            children = (
                session.query(ChildModel)
                .filter_by(generatedCode=code)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .all()
            )

            if len(children):
                resp = make_response(jsonify({"message": "child was already here!"}), 500)
                session.close()
                return resp

            avatar_path, voice_path = "wrong avatar", "wrong voice"

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
            voice_url = voice_path

            created_at = datetime.now()
            last_update = datetime.now()

            new_child = ChildModel(
                phoneNumber=phone_number,
                nationality=nationality,
                avatarUrl=avatar_url,
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
                id_social_worker=social_worker_id,
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

            if file1.filename == "":
                resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY VOICE!"}), 500)

                session.close()
                return resp

            if file2.filename == "":
                resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY AVATAR!"}), 500)

                session.close()
                return resp

            if file1 and allowed_voice(file1.filename):
                # filename1 = secure_filename(file1.filename)
                filename1 = code + "." + file1.filename.split(".")[-1]

                temp_voice_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    str(new_child.id) + "-child"
                )

                if not os.path.isdir(temp_voice_path):
                    os.makedirs(temp_voice_path, exist_ok=True)

                voice_path = os.path.join(
                    temp_voice_path, str(new_child.id) + "-voice_" + filename1
                )
                file1.save(voice_path)

            if file2 and allowed_image(file2.filename):
                # filename2 = secure_filename(file2.filename)
                filename2 = code + "." + file2.filename.split(".")[-1]

                temp_avatar_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], str(new_child.id) + "-child"
                )

                if not os.path.isdir(temp_avatar_path):
                    os.mkdir(temp_avatar_path)

                temp_need_path = os.path.join(temp_avatar_path, "needs")

                if not os.path.isdir(temp_need_path):
                    os.mkdir(temp_need_path)

                avatar_path = os.path.join(
                    temp_avatar_path, str(new_child.id) + "-avatar_" + filename2
                )
                file2.save(avatar_path)

            new_child.avatarUrl = avatar_path
            new_child.voiceUrl = voice_path

            new_child.ngo_relation.childrenCount += 1
            new_child.social_worker_relation.childCount += 1

            session.commit()

            resp = make_response(jsonify({"message": "CHILD ADDED SUCCESSFULLY!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildFamilyMembers(Resource):
    @swag_from("./docs/child/family.yml")
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            family = (
                session.query(FamilyModel)
                .filter_by(isDeleted=False)
                .filter_by(id_child=child_id)
                .first()
            )
            members = (
                session.query(UserFamilyModel)
                .filter_by(id_family=family.id)
                .filter_by(isDeleted=False)
                .all()
            )

            family_res = {}
            for member in members:
                user = (
                    session.query(UserModel)
                    .filter_by(isDeleted=False)
                    .filter_by(id=member.id_user)
                    .first()
                )
                user_data = obj_to_dict(user)
                user_data["Role"] = member.userRole
                family_res[str(user.id)] = user_data

            resp = make_response(jsonify(family_res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class DeleteUserFromChildFamily(Resource):
    @swag_from("./docs/child/delete_member.yml")
    def patch(self, user_id, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            family = (
                session.query(FamilyModel)
                .filter_by(id_child=child_id)
                .filter_by(isDeleted=False)
                .first()
            )
            user = (
                session.query(UserFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(id_family=family.id)
                .filter_by(isDeleted=False)
                .first()
            )
            participation = (
                session.query(NeedFamilyModel)
                .filter_by(id_user=user_id)
                .filter_by(id_family=user_id)
                .filter_by(isDeleted=False)
                .all()
            )

            for participate in participation:
                participate.isDeleted = True

            family.family_child_relation.sayFamilyCount -= 1
            user.isDeleted = True

            session.commit()

            resp = make_response(jsonify({"message": "DELETED SUCCESSFULLY!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class UpdateChildById(Resource):
    @swag_from("./docs/child/update.yml")
    def patch(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            primary_child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .first()
            )

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

            primary_child.lastUpdate = datetime.now()

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
    @swag_from("./docs/child/delete.yml")
    def patch(self, child_id):
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
                    .all()
                )

                for need in needs:
                    need.isDeleted = True

                child.isDeleted = True
                family.isDeleted = True
                child.social_worker_relation.currentChildCount -= 1
                child.ngo_relation.currentChildrenCount -= 1

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


class GetChildrenByBirthPlace(Resource):
    @swag_from("./docs/child/birthplace.yml")
    def get(self, birth_place):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            children = (
                session.query(ChildModel)
                .filter_by(birthPlace=birth_place)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .all()
            )

            res = {}
            for child in children:
                if child.isConfirmed:
                    res[str(child.id)] = get_child_by_id(session, child.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildrenByBirthDate(Resource):
    @swag_from("./docs/child/birth_date.yml")
    def get(self, birth_date, is_after):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            if is_after.lower() == "true":
                children = (
                    session.query(ChildModel)
                    .filter(ChildModel.birthDate >= birth_date)
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=True)
                    .filter_by(isMigrated=False)
                    .all()
                )

            else:
                children = (
                    session.query(ChildModel)
                    .filter(ChildModel.birthDate <= birth_date)
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=True)
                    .filter_by(isMigrated=False)
                    .all()
                )

            res = {}
            for child in children:
                if child.isConfirmed:
                    res[str(child.id)] = get_child_by_id(session, child.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildrenByNationality(Resource):
    @swag_from("./docs/child/nationality.yml")
    def get(self, nationality):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            children = (
                session.query(ChildModel)
                .filter_by(nationality=nationality)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .all()
            )

            res ={}
            for child in children:
                if child.isConfirmed:
                    res[str(child.id)] = get_child_by_id(session, child.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildByNgoId(Resource):
    @swag_from("./docs/child/ngo.yml")
    def get(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'message': 'major error occurred!'}

        try:
            children = (
                session.query(ChildModel)
                .filter_by(id_ngo=ngo_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .all()
            )

            res = {}
            for child in children:
                if child.isConfirmed:
                    res[str(child.id)] = get_child_by_id(session, child.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildBySocialWorkerId(Resource):
    @swag_from("./docs/child/social_worker.yml")
    def get(self, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            children = (
                session.query(ChildModel)
                .filter_by(id_social_worker=social_worker_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=True)
                .filter_by(isMigrated=False)
                .all()
            )

            res = {}
            for child in children:
                if child.isConfirmed:
                    res[str(child.id)] = get_child_by_id(session, child.id)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildUrgentNeedsById(Resource):
    @swag_from("./docs/child/urgent.yml")
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_child_need(session, child_id, urgent=True)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetAllChildrenUrgentNeeds(Resource):
    @swag_from("./docs/child/all_urgent.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            children = (
                session.query(ChildModel)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=True)
                .all()
            )

            result = {}
            for child in children:
                result[str(child.id)] = get_child_need(session, child.id, urgent=True)

            resp = make_response(jsonify(result), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class ConfirmChild(Resource):
    @swag_from("./docs/child/confirm.yml")
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
                .first()
            )
            # print(child.migratedId)
            # print(type(child.migratedId))

            if child.migratedId is None:
                primary_child = child

                if primary_child.isConfirmed:
                    resp = make_response(jsonify({"message": "child has already been confirmed!"}), 500)
                    session.close()
                    return resp

                primary_child.isConfirmed = True
                primary_child.confirmUser = social_worker_id
                primary_child.confirmDate = datetime.now()

                primary_child.ngo_relation.currentChildrenCount += 1

                primary_child.social_worker_relation.currentChildCount += 1

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
                secondary_child.confirmDate = datetime.now()

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
                    secondary_child.social_worker_relation.ngo.id
                    != primary_child.id_ngo
                ):
                    previous_ngo = (
                        session.query(NgoModel)
                        .filter_by(id=primary_child.id_ngo)
                        .filter_by(isDeleted=False)
                        .first()
                    )

                    secondary_child.social_worker_relation.ngo.childrenCount += 1
                    secondary_child.social_worker_relation.ngo.currentChildrenCount += 1
                    previous_ngo.currentChildrenCount -= 1

                secondary_child.social_worker_relation.childCount += 1
                secondary_child.social_worker_relation.currentChildCount += 1
                secondary_child.social_worker_relation.needCount += len(needs)
                secondary_child.social_worker_relation.currentNeedCount += len(needs)

                primary_child.social_worker_relation.currentChildCount -= 1
                primary_child.social_worker_relation.currentNeedCount -= len(needs)

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
                    need.need_relation.imageUrl = need_dump[str(need.id_need)]

                session.commit()

            resp = make_response(jsonify({"message": "child confirmed successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildGeneratedCode(Resource):
    @swag_from("./docs/child/code.yml")
    def get(self, child_id):
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

            resp = make_response(jsonify({"ChildGeneratedCode": child.generatedCode}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetChildByGeneratedCode(Resource):
    @swag_from("./docs/child/by_code.yml")
    def get(self, generated_code):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child = (
                session.query(ChildModel)
                .filter_by(generatedCode=generated_code)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            res = get_child_by_id(session, child.id, confirm=2)
            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class MigrateChild(Resource):
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
                lastUpdate=datetime.now(),
                isConfirmed=False,
                generatedCode=social_worker.generatedCode
                + format(social_worker.childCount + 1, "04d"),
                isMigrated=False,
                migratedId=child.id,
                migrateDate=datetime.now(),
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


class GetMigratedChildHistory(Resource):
    cache = {}

    def migrate_history(self, child, session):
        if child.migratedId is not None:
            previous = (
                session.query(ChildModel)
                .filter_by(isDeleted=False)
                .filter_by(id=child.migratedId)
                .filter_by(isMigrated=True)
                .filter_by(isConfirmed=True)
                .first()
            )
            self.cache[str(previous.id)] = get_child_by_id(session, previous.id, is_migrate=True, confirm=2)
            self.migrate_history(previous, session)
        else:
            return

        return

    @swag_from("./docs/child/history.yml")
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child = (
                session.query(ChildModel)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(id=child_id)
                .filter_by(isConfirmed=True)
                .first()
            )

            if not child:
                resp = make_response(jsonify({"message": "no such child exist!"}), 500)
                session.close()
                return resp

            self.migrate_history(child, session)

            resp = make_response(jsonify(self.cache), 200)
            self.cache = {}

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
api.add_resource(GetChildrenOfUserByUserId, "/api/v2/child/user/userId=<user_id>")
api.add_resource(GetAllChildren, "/api/v2/child/all/confirm=<confirm>")
api.add_resource(GetChildNeeds, "/api/v2/child/need/childId=<child_id>")
api.add_resource(GetChildDoneNeeds, "/api/v2/child/need/done/childId=<child_id>")
api.add_resource(
    GetChildNeedsByCategory, "/api/v2/child/need/childId=<child_id>&category=<category>"
)
api.add_resource(GetChildSayName, "/api/v2/child/sayName/childId=<child_id>")
api.add_resource(GetChildFamilyId, "/api/v2/child/family/childId=<child_id>")
api.add_resource(GetChildAvatarUrl, "/api/v2/child/avatar/childId=<child_id>")
api.add_resource(GetChildCreditSpent, "/api/v2/child/creditSpent/childId=<child_id>")
api.add_resource(
    AddChild, "/api/v2/child/add/socialWorkerId=<social_worker_id>&ngoId=<ngo_id>"
)
api.add_resource(
    GetChildFamilyMembers, "/api/v2/child/family/members/childId=<child_id>"
)
api.add_resource(
    DeleteUserFromChildFamily,
    "/api/v2/child/family/delete/userId=<user_id>&childId=<child_id>",
)
api.add_resource(UpdateChildById, "/api/v2/child/update/childId=<child_id>")
api.add_resource(DeleteChildById, "/api/v2/child/delete/childId=<child_id>")
api.add_resource(GetChildrenByBirthPlace, "/api/v2/child/birthPlace=<birth_place>")
api.add_resource(
    GetChildrenByBirthDate, "/api/v2/child/date=<birth_date>&isAfter=<is_after>"
)
api.add_resource(GetChildrenByNationality, "/api/v2/child/nationality=<nationality>")
api.add_resource(GetChildByNgoId, "/api/v2/child/ngoId=<ngo_id>")
api.add_resource(
    GetChildBySocialWorkerId, "/api/v2/child/socialWorkerId=<social_worker_id>"
)
api.add_resource(
    GetChildUrgentNeedsById, "/api/v2/child/need/urgent/childId=<child_id>"
)
api.add_resource(GetAllChildrenUrgentNeeds, "/api/v2/child/need/urgent/all")
api.add_resource(
    ConfirmChild,
    "/api/v2/child/confirm/childId=<child_id>&socialWorkerId=<social_worker_id>",
)
api.add_resource(
    GetChildGeneratedCode, "/api/v2/child/generatedCode/childId=<child_id>"
)
api.add_resource(
    GetChildByGeneratedCode, "/api/v2/child/generatedCode=<generated_code>"
)
api.add_resource(
    MigrateChild,
    "/api/v2/child/migrate/childId=<child_id>&socialWorkerId=<social_worker_id>",
)
api.add_resource(
    GetMigratedChildHistory, "/api/v2/child/migrate/history/childId=<child_id>"
)
