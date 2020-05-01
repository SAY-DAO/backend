from collections import OrderedDict

import ujson
from dictdiffer import diff
from flask import json as json_
from sqlalchemy import or_

from . import *
from say.models import session, obj_to_dict, commit
from say.models.activity_model import Activity
from say.models.child_model import Child
from say.models.child_need_model import ChildNeed
from say.models.need_family_model import NeedFamily
from say.models.family_model import Family
from say.models.need_model import Need
from say.models.social_worker_model import SocialWorker
from say.models.user_family_model import UserFamily
from say.tasks import update_need


"""
Need APIs
"""


def filter_by_privilege(query):  # TODO: priv
    user_role = get_user_role()
    user_id = get_user_id()
    ngo_id = get_sw_ngo_id()

    if user_role in [SOCIAL_WORKER, COORDINATOR]:
        query = query \
            .join(Child) \
            .filter(or_(
                Child.id_social_worker==user_id,
                Child.id==DEFAULT_CHILD_ID,
             ))

    elif user_role in [NGO_SUPERVISOR]:
        query = query \
            .join(Child) \
            .join(SocialWorker) \
            .filter(or_(
                SocialWorker.id_ngo==ngo_id,
                Child.id==DEFAULT_CHILD_ID,
             ))

    elif user_role in [USER]:
        query = query \
            .join(Child) \
            .join(Family) \
            .join(UserFamily) \
            .filter(UserFamily.id_user==user_id) \
            .filter(UserFamily.isDeleted==False) \

    return query


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
            needs = session.query(Need) \
                .filter(Need.isDeleted==False) \
                .order_by(Need.doneAt.desc())


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
                    .join(Child) \
                    .join(SocialWorker) \
                    .filter(SocialWorker.id_ngo==ngo_id)

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
            need_query = session.query(Need) \
                .filter_by(isDeleted=False) \
                .filter_by(id=need_id)

            need = filter_by_privilege(need_query).first()

            if need is None:
                resp = HTTP_NOT_FOUND()
                return

            need_dict = obj_to_dict(need)

            need_dict['participants'] = [
                obj_to_dict(p) for p in need.current_participants
            ]
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
    @commit
    @swag_from("./docs/need/update.yml")
    def patch(self, need_id):
        sw_role = get_user_role()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need_query = session.query(Need) \
                .filter_by(id=need_id) \
                .filter_by(isDeleted=False)

            need = filter_by_privilege(need_query).first()

            if need is None:
                resp = HTTP_NOT_FOUND()
                return

            temp = obj_to_dict(need)
            child = need.child

            activity = Activity(
                id_social_worker=get_user_id(),
                model=Need.__tablename__,
                activityCode=11,  # TODO: wrong code
            )
            session.add(activity)

            new_cost = None
            if "cost" in request.form.keys():
                new_cost = int(request.form['cost'].replace(',', ''))

                if (
                    (
                        (sw_role in [SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR]
                            and need.isConfirmed)
                        or need.isDone
                    ) and new_cost != need._cost
                ):

                    resp = make_response(
                        jsonify({"message": "Can not change cost when need is done"}),
                        503,
                    )
                    return

                need.cost = new_cost

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

                if file2 and allowed_receipt(file2.filename):
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
                new_link = request.form["link"]
                if new_link != need.link:
                    need.link = new_link
                    session.flush()
                    update_need.delay(need.id, force=True)

            if "affiliateLinkUrl" in request.form.keys():
                need.affiliateLinkUrl = request.form["affiliateLinkUrl"]

            if "name_translations" in request.form.keys():
                need.name_translations = ujson.loads(
                    request.form["name_translations"],
                )

            if "description_translations" in request.form.keys():
                need.description_translations = ujson.loads(
                    request.form["description_translations"],
                )

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

                purchase_cost = request.form.get('purchase_cost', None)
                if purchase_cost and sw_role in [
                   SUPER_ADMIN, SAY_SUPERVISOR, ADMIN,
                ] and new_status == 3 and need.type == 1:

                    need.purchase_cost = purchase_cost

                if new_status != 5 and new_status - prev_status == 1:
                    if new_status == 4 and need.isReported != True:
                        raise Exception('Need has not been reported to ngo yet')

                    need.status = new_status

                    # FIXME: Is bank_track_id is nullable?
                    if need.type == 0 and new_status == 3 and prev_status == 2:
                        need.bank_track_id = request.form.get(
                            'bankTrackId',
                            None,
                        )

                elif new_status != prev_status:
                    raise ValueError(
                        f'Can not change status from '
                        f'{prev_status} to {new_status}'
                    )

            if need.type == 0 and need.status == 3:
                need.bank_track_id = request.form.get(
                    'bank_track_id',
                    None,
                )

            activity.diff = json_.dumps(list(diff(temp, obj_to_dict(need))))

            session.commit()
            secondary_need = obj_to_dict(need)
            resp = make_response(jsonify(secondary_need), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


class DeleteNeedById(Resource):

    @json
    @commit
    @authorize(SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN,
               SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from('./docs/need/delete.yml')
    def patch(self, need_id):
        need = (
            session.query(Need)
            .filter_by(isDeleted=False)
            .filter_by(id=need_id)
            .first()
        )

        if (need.type == 0 and need.status < 4) or (need.type == 1 and need.status < 5):
            need.status = 0
            need.purchase_cost = 0
            need.refund_extra_credit()

            for participant in need.participants:
                participant.isDeleted = True

            need.isDeleted = True

            return {"message": "need deleted"}
        
        else:
            return {"message": "need has arrived to the child so can not be deleted"}
                


class ConfirmNeed(Resource):

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @swag_from("./docs/need/confirm.yml")
    def patch(self, need_id):
        social_worker_id = get_user_id()

        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            primary_need = (
                session.query(Need)
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

            new_child_need = ChildNeed(
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
                session.query(Child)
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
                allowed_sw_ids_tuple = session.query(SocialWorker.id) \
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

            name_translations = ujson.loads(
                request.form["name_translations"]
            )
            description_translations = ujson.loads(
                request.form["description_translations"],
            )

            is_urgent = True if request.form["isUrgent"] == "true" else False
            need_type = request.form["type"]

            details = request.form.get("details", '')
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

            new_need = Need(
                name_translations=name_translations,
                description_translations=description_translations,
                imageUrl=image_url,
                category=category,
                cost=cost,
                purchase_cost=cost,
                isUrgent=is_urgent,
                affiliateLinkUrl=affiliate_link_url,
                link=link,
                receipts=receipts,
                type=need_type,
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

                if file2 and allowed_receipt(file2.filename):
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

            if new_need.link:
                update_need.delay(new_need.id)

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
