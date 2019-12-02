from collections import OrderedDict
from dictdiffer import diff

# from say.api.child_api import get_child_by_id
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
            # .group_by(PaymentModel.id)
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


class GetNeedById(Resource):
    @swag_from("./docs/need/id.yml")
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(id=need_id)
                .first()
            )

            resp = make_response(jsonify(get_need(need, session)), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetAllNeeds(Resource):
    @swag_from("./docs/need/all.yml")
    def get(self, confirm):
        args = request.args
        done = args.get('done', -1)
        status = args.get('status', None)
        ngo_id = args.get('ngoId', None)
        is_reported = args.get('isReported', None)
        type_ = args.get('type', None)

        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            done = int(done)
            needs = session.query(NeedModel).order_by(NeedModel.doneAt.desc())

            if int(confirm) == 2:
                needs = needs.filter_by(isDeleted=False)

            elif int(confirm) == 1:
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

            else:
                return make_response(jsonify({"message": "wrong input"}), 500)

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
                is_reported = bool(is_reported)
                needs = needs.filter_by(isReported=is_reported)

            if ngo_id:
                ngo_id = int(ngo_id)
                needs = needs \
                    .join(ChildNeedModel) \
                    .join(ChildModel) \
                    .filter(ChildModel.id_ngo==ngo_id)

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

                result['needs'].append(res)

            resp = jsonify(result)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": str(e)}), 500)

        finally:
            session.close()
            return resp


class GetNeedByCategory(Resource):
    @swag_from("./docs/need/category.yml")
    def get(self, category):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            needs = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(category=category)
                .all()
            )

            res = {}
            for need in needs:
                res[str(need.id)] = get_need(need, session)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetNeedByType(Resource):
    @swag_from("./docs/need/type.yml")
    def get(self, need_type):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            needs = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(type=need_type)
                .all()
            )

            res = {}
            for need in needs:
                res[str(need.id)] = get_need(need, session)

            resp = make_response(jsonify(res), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetNeedParticipants(Resource):
    @swag_from("./docs/need/participants.yml")
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )

            resp = make_response(jsonify(get_need(need, session, participants_only=True)), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetNeedReceipts(Resource):
    @swag_from("./docs/need/receipts.yml")
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )

            resp = make_response(jsonify({"NeedReceipts": need.receipts}), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class GetAllUrgentNeeds(Resource):
    @swag_from("./docs/need/all_urgent.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            resp = make_response(jsonify(get_all_urgent_needs(session)), 200)

        except Exception as e:
            print(e)

            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddPaymentForNeed(Resource):
    @swag_from("./docs/need/payment.yml")
    def post(self, need_id, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            amount = int(request.form["amount"])
            created_at = datetime.utcnow()

            need = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(id=need_id)
                .first()
            )

            if not need.isConfirmed:
                resp = make_response(jsonify({"message": "error: need is not confirmed yet!"}), 500)
                session.close()
                return resp

            user = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(id=user_id)
                .first()
            )
            child = need.child
            family = (
                session.query(FamilyModel)
                .filter_by(id_child=child.id_child)
                .filter_by(isDeleted=False)
                .first()
            )

            if (
                session.query(UserFamilyModel)
                .filter_by(isDeleted=False)
                .filter_by(id_family=family.id)
                .filter_by(id_user=user_id)
                .first()
                is None
            ):
                resp = make_response(jsonify({"message": "payment must be added by the child's family!"}), 500)
                session.close()
                return resp

            if amount > need.cost - need.paid:
                resp = make_response(jsonify({"message": f"you can pay {need.cost - need.paid} at most!"}), 500)
                session.close()
                return resp

            elif amount > user.credit:
                resp = make_response(jsonify({"message": f"your credit is less than {amount}! you have {user.credit}."}), 500)
                session.close()
                return resp

            elif amount <= 0:
                resp = make_response(jsonify({"message": "amount can not be 0 or less!"}), 500)
                session.close()
                return resp

            else:
                new_payment = PaymentModel(
                    id_need=need_id,
                    id_user=user_id,
                    amount=amount,
                    createdAt=created_at,
                )

                session.add(new_payment)

                participant = (
                    session.query(NeedFamilyModel)
                    .filter_by(id_need=need_id)
                    .filter_by(id_user=user_id)
                    .filter_by(isDeleted=False)
                    .first()
                )
                if participant is None:
                    new_participant = NeedFamilyModel(
                        id_family=family.id, id_user=user_id, id_need=need_id
                    )

                    session.add(new_participant)

                session.commit()

                user.credit -= amount
                user.spentCredit += amount
                need.paid += amount

                child.spentCredit += amount
                if need.paid == need.cost:
                    need.isDone = True
                    # user.doneNeedCount += 1  # TODO: which one is correct?

                    participants = (
                        session.query(NeedFamilyModel)
                        .filter_by(id_need=need_id)
                        .filter_by(isDeleted=False)
                        .all()
                    )

                    for participate in participants:
                        participate.user.doneNeedCount += 1

                    child.doneNeedCount += 1

                session.commit()

                resp = make_response(jsonify({"message": "payment added successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class UpdateNeedById(Resource):
    @swag_from("./docs/need/update.yml")
    def patch(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )
            temp = obj_to_dict(need)
            child = need.child

            activity = ActivityModel(
                id_social_worker=child.id_social_worker,
                model=NeedModel.__tablename__,
                activityCode=11,
            )
            session.add(activity)

            if "cost" in request.form.keys():
                if need.isDone and int(request.form['cost']) != need._cost:
                    resp = make_response(jsonify({"message": "Can not change cost when need is done"}), 503)
                    return

                # if not need.isConfirmed:
                need._cost = int(request.form["cost"])

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
                        os.mkdir(temp_need_path)


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
                        os.mkdir(temp_need_path)

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

            if "affiliateLinkUrl" in request.form.keys():
                need.affiliateLinkUrl = request.form["affiliateLinkUrl"]

            if "description" in request.form.keys():
                need.description = request.form["description"]

            if "descriptionSummary" in request.form.keys():
                need.descriptionSummary = request.form["descriptionSummary"]

            if "name" in request.form.keys():
                need.name = request.form["name"]

            if "doing_duration" in request.form.keys():
                need.doing_duration = int(request.form["doing_duration"])

            if "details" in request.form.keys():
                need.details = request.form["details"]

            if "delivery_date" in request.form.keys():
                need.delivery_date = request.form["delivery_date"]

            if "status" in request.form.keys():
                new_status = int(request.form["status"])
                prev_status = need.status

                if prev_status >= new_status:
                    pass
                else:
                    need.status = new_status
                    if need.type == 0:  # Service
                        if new_status == 3:
                            need.send_money_to_ngo_email()
                        if new_status == 4:
                            need.send_child_delivery_service_email()
                    if need.type == 1:  # Product
                        if new_status == 3:
                            need.send_purchase_email()
                        if new_status == 4:
                            need.send_child_delivery_product_email()

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
    @swag_from("./docs/need/delete.yml")
    def patch(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )
            children = (
                session.query(ChildNeedModel)
                .filter_by(id_need=need_id)
                .filter_by(isDeleted=False)
                .all()
            )

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
    @swag_from("./docs/need/confirm.yml")
    def patch(self, need_id, social_worker_id, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
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

            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            social_worker = (
                session.query(SocialWorkerModel)
                .filter_by(id=child.id_social_worker)
                .filter_by(isDeleted=False)
                .first()
            )

            primary_need.isConfirmed = True
            primary_need.confirmUser = social_worker_id
            primary_need.confirmDate = datetime.utcnow()

            new_child_need = ChildNeedModel(id_child=child_id, id_need=primary_need.id)

            if social_worker:
                social_worker.needCount += 1
                social_worker.currentNeedCount += 1

            session.add(new_child_need)
            session.commit()

            resp = make_response(jsonify({"message": "need confirmed successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddParticipantToNeed(Resource):
    @swag_from("./docs/need/add_participant.yml")
    def post(self, user_id, need_id, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = make_response(jsonify({"message": "major error occurred!"}), 503)

        try:
            if (
                session.query(UserFamilyModel)
                .filter_by(isDeleted=False)
                .filter_by(id_family=family_id)
                .filter_by(id_user=user_id)
                .first()
                is None
            ):
                resp = make_response(jsonify({"message": "participant must be from the child's family!"}), 500)
                session.close()
                return resp

            new_participant = NeedFamilyModel(
                id_family=family_id, id_user=user_id, id_need=need_id
            )

            session.add(new_participant)
            session.commit()

            resp = make_response(jsonify({"message": "participant added successfully!"}), 200)

        except Exception as e:
            print(e)
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

        finally:
            session.close()
            return resp


class AddNeed(Resource):
    @swag_from("./docs/need/add.yml")
    def post(self, child_id):
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
            debug(f'child: {obj_to_dict(child)}')

            if not child.isConfirmed:
                resp = make_response(jsonify({"message": "error: child is not confirmed yet!"}), 500)
                session.close()
                return resp

            image_path, receipt_path = "wrong path", None

            image_url = image_path
            receipts = receipt_path

            category = int(request.form["category"])
            cost = request.form["cost"]
            name = request.form["name"]
            is_urgent = True if request.form["isUrgent"] == "true" else False
            need_type = request.form["type"]
            description = request.form["description"]
            description_summary = request.form["descriptionSummary"]
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
                createdAt=created_at,
                category=category,
                cost=cost,
                isUrgent=is_urgent,
                descriptionSummary=description_summary,
                description=description,
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

            if "imageUrl" not in request.files:
                resp = make_response(jsonify({"message": "ERROR OCCURRED IN FILE UPLOADING!"}), 500)
                session.close()
                return resp

            file = request.files["imageUrl"]
            if file.filename == "":
                resp = make_response(jsonify({"message": "ERROR OCCURRED --> EMPTY FILE!"}), 500)
                session.close()
                return resp

            child_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                str(child.id) + "-child",
            )

            if not os.path.isdir(child_path):
                os.makedirs(child_path, exist_ok=True)

            needs_path = os.path.join(child_path, "needs")
            if not os.path.isdir(needs_path):
                os.makedirs(needs_path, exist_ok=True)

            need_dir = str(new_need.id) + "-need"

            if file and allowed_image(file.filename):
                # filename = secure_filename(file.filename)
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

            debug(f'final need: {obj_to_dict(new_need)}')

            # else:
            #     receipt_path = None

            session.commit()

            resp = make_response(jsonify(obj_to_dict(new_need)), 200)

        except Exception as e:
            resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)
            print(e)

        finally:
            session.close()
            return resp


# class Foo(Resource):
#     def get(self):
#         session_maker = sessionmaker(db)
#         session = session_maker()
#         resp = make_response(jsonify({"message": "major error occurred!"}), 503)

#         try:
#             children = (
#                 session.query(ChildModel)
#                 .filter_by(isDeleted=False)
#                 .filter_by(isMigrated=False)
#                 .filter_by(isConfirmed=True)
#                 .all()
#             )
#             users = (
#                 session.query(UserModel)
#                 .filter_by(isDeleted=False)
#                 .all()
#             )
#             for c in children:
#                 child = get_child_by_id(session, c.id, with_need=True)
#                 for n in child["Needs"].keys():
#                     if child["Needs"][n].isDone:
#                         c.doneNeedCount += 1

#             for u in users:
#                 payments = (
#                     session.query(PaymentModel)
#                     .filter_by(id_user=u.id)
#                     .all()
#                 )
#                 for p in payments:
#                     u.spentCredit += p.amount

#             resp = make_response(dict(message="ماست‌مالی انجام شد :)"), 200)

#         except Exception as e:
#             print(e)
#             resp = make_response(jsonify({"message": "ERROR OCCURRED"}), 500)

#         finally:
#             session.close()
#             return resp


"""
API URLs
"""

# api.add_resource(Foo, "/api/v2/need/foo")
api.add_resource(GetNeedById, "/api/v2/need/needId=<need_id>")
api.add_resource(GetAllNeeds, "/api/v2/need/all/confirm=<confirm>")
api.add_resource(GetNeedByCategory, "/api/v2/need/category=<category>")
api.add_resource(GetNeedByType, "/api/v2/need/type=<need_type>")
api.add_resource(GetNeedParticipants, "/api/v2/need/participants/needId=<need_id>")
api.add_resource(GetNeedReceipts, "/api/v2/need/receipts/needId=<need_id>")
api.add_resource(GetAllUrgentNeeds, "/api/v2/need/urgent/all")
api.add_resource(
    AddPaymentForNeed, "/api/v2/need/payment/needId=<need_id>&userId=<user_id>"
)
api.add_resource(UpdateNeedById, "/api/v2/need/update/needId=<need_id>")
api.add_resource(DeleteNeedById, "/api/v2/need/delete/needId=<need_id>")
api.add_resource(
    ConfirmNeed,
    "/api/v2/need/confirm/needId=<need_id>&socialWorkerId=<social_worker_id>&childId=<child_id>",
)
api.add_resource(
    AddParticipantToNeed,
    "/api/v2/need/participants/add/needId=<need_id>&userId=<user_id>&familyId=<family_id>",
)
api.add_resource(AddNeed, "/api/v2/need/add/childId=<child_id>")
