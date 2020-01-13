from collections import OrderedDict
from dictdiffer import diff

from sqlalchemy import func, or_

# from say.api.child_api import get_child_by_id
from say.models import session, obj_to_dict
from say.models.activity_model import ActivityModel
from say.models.child_model import ChildModel
from say.models.child_need_model import ChildNeedModel
from say.models.family_model import FamilyModel
from say.models.need_family_model import NeedFamilyModel
from say.models.need_model import NeedModel
from say.models.payment_model import PaymentModel
from say.models.social_worker_model import SocialWorkerModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel
from . import *

"""
Need APIs
"""


def filter_by_privilege(query):  # TODO: priv
    user_role = get_user_role()
    user_id = get_user_id()
    ngo_id = get_sw_ngo_id()

    if user_role in [SOCIAL_WORKER, COORDINATOR]:
        query = query \
            .join(ChildModel) \
            .filter(or_(
                ChildModel.id_social_worker==user_id,
                ChildModel.id==DEFAULT_CHILD_ID,
             ))

    elif user_role in [NGO_SUPERVISOR]:
        query = query \
            .join(ChildModel) \
            .join(SocialWorkerModel) \
            .filter(or_(
                SocialWorkerModel.id_ngo==ngo_id,
                ChildModel.id==DEFAULT_CHILD_ID,
             ))

    elif user_role in [USER]:
        query = query \
            .join(ChildModel) \
            .join(FamilyModel) \
            .join(UserFamilyModel) \
            .filter(UserFamilyModel.id_user==user_id) \
            .filter(UserFamilyModel.isDeleted==False) \

    return query


def get_all_urgent_needs(session):
    needs = (
        session.query(NeedModel)
        .filter_by(isUrgent=True)
        .filter_by(isDeleted=False)
        .filter_by(isConfirmed=True)
        .all()
    )

    needs_data = {}
    for need in needs:
        needs_data[str(need.id)] = get_need(need, session)

    return needs_data


def get_need(need, session, participants_only=False, with_participants=True, with_child_id=True):
    need_data = obj_to_dict(need)

    if not with_participants and not with_child_id:
        return need_data

    child = need.child
    need_data['ChildName'] = child.sayName

    if not with_participants and with_child_id:
        return need_data

    participant_ids = session.query(NeedFamilyModel).filter_by(id_need=need.id).filter_by(isDeleted=False).all()
    ids = [p.id_user for p in participant_ids]

    participants = (
        session.query(UserFamilyModel)
        .filter(UserFamilyModel.id_user.in_(ids))
        # .filter_by(isDeleted=False)
    )

#    if len(participant_ids) > 0:
#        family = list(participant_ids)[0].id_family
#        participants = participants.filter_by(id_family=family)
#
#    participants = participants.all()

    if len(participant_ids) > 0:
        family_id = list(participant_ids)[0].id_family
        participants = participants.filter_by(id_family=family_id)

    users = {}
    for participant in participants:
        temp_participant = obj_to_dict(participant)

        temp_participant['Contribution'] = (
            (session.query(func.sum(PaymentModel.amount))
            .filter_by(id_user=participant.id_user)
            .filter_by(id_need=need.id)
            .filter_by(is_verified=True)
            .group_by(PaymentModel.id_user, PaymentModel.id_need)
            .first())[0]
        )

        user_info = (
            session.query(UserModel.avatarUrl, UserModel.firstName, UserModel.lastName)
            .filter_by(id=participant.id_user)
            .filter_by(isDeleted=False)
            .first()
        )
        temp_participant['userAvatar'] = user_info[0]
        temp_participant['userFirstName'] = user_info[1]
        temp_participant['userLastName'] = user_info[2]

        users[str(participant.id_user)] = temp_participant

    if participants_only:
        return users

    need_data["Participants"] = users

    return need_data


class GetAllNeeds(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/need/all.yml")
    def get(self, confirm):
        sw_role = get_user_role()
        args = request.args
        done = args.get('done', -1)
        status = args.get('status', None)
        ngo_id = args.get('ngoId', None)

        is_reported = args.get('isReported', None)
        type_ = args.get('type', None)

        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            done = int(done)
            needs = session.query(NeedModel) \
                .filter(NeedModel.isDeleted==False) \
                .order_by(NeedModel.doneAt.desc())


            if int(confirm) == 1:
                needs = (
                    needs
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=True)
                )

            elif int(confirm) == 0:
                needs = (
                    needs
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=False)
                )

            if done == 1:
                needs = needs.filter_by(isDone=True)

            elif done == 0:
                needs = needs.filter_by(isDone=False)

            if type_:
                type_ = int(type_)
                needs = needs.filter_by(type=type_)

            if status:
                status = int(status)
                needs = needs.filter_by(status=status)

            if is_reported:
                is_reported = bool(int(is_reported))
                needs = needs.filter_by(isReported=is_reported)

            if ngo_id and sw_role in [
                SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
            ]:
                ngo_id = int(ngo_id)
                needs = needs \
                    .join(ChildModel) \
                    .join(SocialWorkerModel) \
                    .filter(SocialWorkerModel.id_ngo==ngo_id)

            needs = filter_by_privilege(needs)

            result = OrderedDict(
                totalCount=needs.count(),
                needs=[],
            )
            for need in needs:
                res = obj_to_dict(need)

                ngo = need.child.ngo
                child = need.child

                res['ngoId'] = ngo.id
                res['ngoName'] = ngo.name
                res['ngoAddress'] = ngo.postalAddress
                res['childGeneratedCode'] = child.generatedCode
                res['childFirstName'] = child.firstName
                res['childLastName'] = child.lastName
                res['childSayName'] = child.sayName

                result['needs'].append(res)

            resp = jsonify(result)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


class GetNeedById(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN, USER)  # TODO: priv
    @swag_from("./docs/need/id.yml")
    def get(self, need_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need_query = session.query(NeedModel) \
                .filter_by(isDeleted=False) \
                .filter_by(id=need_id)

            need = filter_by_privilege(need_query).first()

            if need is None:
                resp = HTTP_NOT_FOUND()
                return

            need_dict = obj_to_dict(need)

            need_dict['Participants'] = get_need(
                need,
                session,
                participants_only=True,
            )

            resp = make_response(
                jsonify(need_dict),
                200,
            )

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class UpdateNeedById(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/need/update.yml")
    def patch(self, need_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need_query = session.query(NeedModel) \
                .filter_by(id=need_id) \
                .filter_by(isDeleted=False)

            need = filter_by_privilege(need_query).first()

            if need is None:
                resp = HTTP_NOT_FOUND()
                return

            temp = obj_to_dict(need)
            child = need.child

            activity = ActivityModel(
                id_social_worker=get_user_id(),
                model=NeedModel.__tablename__,
                activityCode=11,  # TODO: wrong code
            )
            session.add(activity)

            if "cost" in request.form.keys():
                if need.isDone and int(request.form['cost']) != need._cost:
                    resp = make_response(jsonify({"message": "Can not change cost when need is done"}), 503)
                    return

                # if not need.isConfirmed:
                need.cost = request.form["cost"]

                # else:
                #     resp = make_response(jsonify({"message": "error: cannot change cost for confirmed need!"}), 500)
                #     session.close()
                #     return resp

            if "imageUrl" in request.files.keys():
                file = request.files["imageUrl"]

                if file.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                    session.close()
                    return resp

                if file and allowed_image(file.filename):
                    # filename = secure_filename(file.filename)
                    filename = str(need.id) + "." + file.filename.split(".")[-1]

                    temp_need_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(child.id) + "-child"
                    )
                    temp_need_path = os.path.join(temp_need_path, "needs")
                    temp_need_path = os.path.join(
                        temp_need_path, str(need.id) + "-need"
                    )

                    if not os.path.isdir(temp_need_path):
                        os.makedirs(temp_need_path, exist_ok=True)

                    for obj in os.listdir(temp_need_path):
                        check = str(need.id) + "-image"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_need_path, obj))

                    need.imageUrl = os.path.join(
                        temp_need_path, str(need.id) + "-image_" + filename
                    )
                    file.save(need.imageUrl)
                    need.imageUrl = '/' + need.imageUrl

            if "receipts" in request.files.keys():
                file2 = request.files["receipts"]

                if file2.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    # filename = secure_filename(file2.filename)
                    if need.receipts is not None:
                        filename = (
                            str(len(need.receipts.split(",")))
                            + "."
                            + file2.filename.split(".")[-1]
                        )
                    else:
                        filename = str(0) + "." + file2.filename.split(".")[-1]

                    temp_need_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(child.id) + "-child"
                    )
                    temp_need_path = os.path.join(temp_need_path, "needs")
                    temp_need_path = os.path.join(
                        temp_need_path, str(need.id) + "-need"
                    )
                    if not os.path.isdir(temp_need_path):
                        os.makedirs(temp_need_path, exist_ok=True)

                    receipt_path = os.path.join(
                        temp_need_path, str(need.id) + "-receipt_" + filename
                    )
                    file2.save(receipt_path)

                    receipt_path = '/' + receipt_path
                    if need.receipts is None:
                        need.receipts = str(receipt_path)
                    else:
                        need.receipts += "," + str(receipt_path)


            if "category" in request.form.keys():
                need.category = int(request.form["category"])

            if "type" in request.form.keys():
                need.type = int(request.form["type"])

            if "isUrgent" in request.form.keys():
                need.isUrgent = (
                    True if request.form["isUrgent"] == "true" else False
                )

            if "link" in request.form.keys():
                need.link = request.form["link"]

                from say.tasks import update_need
                update_need.delay(need.id)

            if "affiliateLinkUrl" in request.form.keys():
                need.affiliateLinkUrl = request.form["affiliateLinkUrl"]

            if "description" in request.form.keys():
                need.description = request.form["description"]

            if "descriptionSummary" in request.form.keys():
                need.descriptionSummary = request.form["descriptionSummary"]

            if "name" in request.form.keys():
                need.name = request.form["name"]

            if "description_fa" in request.form.keys():
                need.description_fa = request.form["description_fa"]

            if "descriptionSummary_fa" in request.form.keys():
                need.descriptionSummary_fa = request.form["descriptionSummary_fa"]

            if "name_fa" in request.form.keys():
                need.name_fa = request.form["name_fa"]

            if "doing_duration" in request.form.keys():
                need.doing_duration = int(request.form["doing_duration"])

            if "details" in request.form.keys():
                need.details = request.form["details"]

            if request.form.get("expected_delivery_date"):
               if not(2 <= need.status <= 3):
                  raise Exception(
                      'Expected delivery date can not changed in this status'
                  )
               need.isReported = False
               need.expected_delivery_date = parse_datetime(
                   request.form["expected_delivery_date"]
               )

            if "status" in request.form.keys():
                new_status = int(request.form["status"])
                prev_status = need.status

                # For making sure that sending same status has no effect
                if new_status == prev_status:
                    pass

                elif new_status != 5 and new_status - prev_status == 1:
                    if new_status == 4 and need.isReported != True:
                        raise Exception('Need has not been reported to ngo yet')

                    need.status = new_status
                    if need.type == 0:  # Service
                        if new_status == 3:
                            need.ngo_delivery_date = datetime.utcnow()
                            need.send_money_to_ngo_email()

                        if new_status == 4:
                            need.child_delivery_date = datetime.utcnow()
                            need.send_child_delivery_service_email()

                    if need.type == 1:  # Product
                        if new_status == 3:
                            need.purchase_date = datetime.utcnow()
                            need.send_purchase_email()

                        if new_status == 4:
                            need.ngo_delivery_date = parse_datetime(
                                request.form.get('ngo_delivery_date')
                            )

                            if not(
                                need.expected_delivery_date
                                <= need.ngo_delivery_date <=
                                datetime.utcnow()
                            ):
                                raise Exception('Invalid ngo_delivery_date')

                            need.send_child_delivery_product_email()

                else:
                    raise ValueError(
                        f'Can not change status from '
                        f'{prev_status} to {new_status}'
                    )

            need.lastUpdate = datetime.utcnow()

            secondary_need = obj_to_dict(need)

            activity.diff = json.dumps(list(diff(temp, obj_to_dict(need))))

            session.commit()
            resp = make_response(jsonify(secondary_need), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


class DeleteNeedById(Resource):

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/need/delete.yml")
    def patch(self, need_id):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need_query = session.query(NeedModel) \
                .filter_by(id=need_id) \
                .filter_by(isDeleted=False)

            need = filter_by_privilege(need_query).first()

            if need.isConfirmed:
                if need.paid != 0:
                    resp = make_response(jsonify({"message": "error in deletion"}), 500)
                    session.close()
                    return resp

            need.isDeleted = True
            session.commit()

            resp = make_response(jsonify({"message": "need deleted successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class ConfirmNeed(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/need/confirm.yml")
    def patch(self, need_id):
        social_worker_id = get_user_id()

        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            primary_need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if primary_need.isConfirmed:
                resp = make_response(jsonify({"message": "need has already been confirmed!"}), 500)
                session.close()
                return resp

            child = primary_need.child

            primary_need.isConfirmed = True
            primary_need.confirmUser = social_worker_id
            primary_need.confirmDate = datetime.utcnow()

            new_child_need = ChildNeedModel(
                id_child=child.id,
                id_need=primary_need.id,
            )

            child.social_worker.needCount += 1
            child.social_worker.currentNeedCount += 1

            session.add(new_child_need)
            session.commit()

            resp = make_response(jsonify({"message": "need confirmed successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddNeed(Resource):

    def check_privilege(self, sw_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id():
                return HTTP_PERMISION_DENIED()

        elif sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids:
                return HTTP_PERMISION_DENIED()

        return None

    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/need/add.yml")
    def post(self):
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            child_id = int(request.form["child_id"])
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            sw_id = int(request.form.get("sw_id", get_user_id()))
            sw_role = get_user_role()

            allowed_sw_ids = []
            if sw_role in [NGO_SUPERVISOR]:
                allowed_sw_ids_tuple = session.query(SocialWorkerModel.id) \
                    .filter_by(isDeleted=False) \
                    .filter_by(id_ngo=get_sw_ngo_id()) \
                    .distinct() \
                    .all()

                allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

            error = self.check_privilege(sw_id, allowed_sw_ids)
            if error:
                resp = error
                return

            if not child.isConfirmed:
                resp = make_response(jsonify({"message": "error: child is not confirmed yet!"}), 500)
                session.close()
                return resp

            image_path, receipt_path = "wrong path", None

            image_url = image_path
            receipts = receipt_path

            category = int(request.form["category"])
            cost = request.form["cost"].replace(',', '')
            name = request.form["name"]
            name_fa = request.form.get('name_fa', None)
            is_urgent = True if request.form["isUrgent"] == "true" else False
            need_type = request.form["type"]
            description = request.form["description"]
            description_fa = request.form.get('description_fa', None)
            description_summary = request.form["descriptionSummary"]
            description_summary_fa = request.form.get(
                'descriptionSummary_fa',
                None,
            )
            details = request.form.get("details", '')
            created_at = datetime.utcnow()
            last_update = datetime.utcnow()
            link = request.form.get('link', None)

            if "affiliateLinkUrl" in request.form.keys():
                affiliate_link_url = request.form["affiliateLinkUrl"]
            else:
                affiliate_link_url = None

            if "doing_duration" in request.form.keys():
                doing_duration = int(request.form["doing_duration"])
            else:
                doing_duration = 5

            new_need = NeedModel(
                imageUrl=image_url,
                name=name,
                name_fa=name_fa,
                createdAt=created_at,
                category=category,
                cost=cost,
                isUrgent=is_urgent,
                descriptionSummary=description_summary,
                descriptionSummary_fa=description_summary_fa,
                description=description,
                description_fa=description_fa,
                affiliateLinkUrl=affiliate_link_url,
                link=link,
                receipts=receipts,
                type=need_type,
                lastUpdate=last_update,
                child=child,
                doing_duration=doing_duration,
                details=details,
            )

            session.add(new_need)
            session.flush()

            child_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                str(child.id) + "-child",
            )
            needs_path = os.path.join(child_path, "needs")
            if not os.path.isdir(child_path):
                os.makedirs(child_path, exist_ok=True)

            if not os.path.isdir(needs_path):
                os.makedirs(needs_path, exist_ok=True)

            need_dir = str(new_need.id) + "-need"

            if "imageUrl" in request.files:
                file = request.files["imageUrl"]
                if not allowed_image(file.filename):
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                    return

                filename = str(new_need.id) + "." + file.filename.split(".")[-1]
                temp_need_path = os.path.join(needs_path, need_dir)

                if not os.path.isdir(temp_need_path):
                    os.makedirs(temp_need_path, exist_ok=True)

                image_path = os.path.join(
                    temp_need_path, str(new_need.id) + "-image_" + filename
                )

                file.save(image_path)
                new_need.imageUrl = '/' + image_path


            if "receipts" in request.files.keys():
                file2 = request.files["receipts"]
                if file2.filename == "":
                    resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    filename = secure_filename(file2.filename)
                    # filename = str(0) + "." + file2.filename.split(".")[-1]

                    temp_need_path = os.path.join(
                        temp_need_path, str(new_need.id) + "-need"
                    )

                    if not os.path.isdir(temp_need_path):
                        os.makedirs(temp_need_path, exist_ok=True)

                    receipt_path = os.path.join(
                        temp_need_path, str(new_need.id) + "-receipt_" + filename
                    )

                    file2.save(receipt_path)
                    new_need.receipts = '/' + receipt_path

            session.commit()

            resp = make_response(jsonify(obj_to_dict(new_need)), 200)

        except Exception as e:
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)
            print(e)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetNeedById, "/api/v2/need/needId=<need_id>")
api.add_resource(GetAllNeeds, "/api/v2/need/all/confirm=<confirm>")
api.add_resource(UpdateNeedById, "/api/v2/need/update/needId=<need_id>")
api.add_resource(DeleteNeedById, "/api/v2/need/delete/needId=<need_id>")
api.add_resource(
    ConfirmNeed,
    "/api/v2/need/confirm/needId=<need_id>",
)
api.add_resource(AddNeed, "/api/v2/need/")
