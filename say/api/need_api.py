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

    needs_data = "{"
    for need in needs:
        needs_data += f'"{str(need.id)}": {get_need(need, session)}, '

    return needs_data[:-2] + "}" if len(needs_data) != 1 else "{}"


def get_need(need, session, participants_only=False, with_participants=True, with_child_id=True):
    if need.isConfirmed:

        need_data = obj_to_dict(need)

        if not with_participants and not with_child_id:
            need_data = utf8_response(need_data)
            return need_data

        child = session.query(ChildNeedModel).filter_by(id_need=need.id).filter_by(isDeleted=False).first()
        need_data['ChildId'] = child.id_child
        need_data = utf8_response(need_data)

        if not with_participants and with_child_id:
            return need_data

        participant_ids = session.query(NeedFamilyModel).filter_by(id_need=need.id).filter_by(isDeleted=False).all()
        ids = [p.id_user for p in participant_ids]
        participants = session.query(UserModel).filter(UserModel.id.in_(ids)).filter_by(isDeleted=False).all()

        users = '{'
        for participant in participants:
            # user = session.query(UserModel).filter_by(isDeleted=False).filter_by(id=participant.id_user).first()
            users += f'"{str(participant.id)}": {utf8_response(obj_to_dict(participant))}, '

        users_data = users[:-2] + "}" if len(users) != 1 else "{}"

        if participants_only:
            return users_data

        need_data = need_data[:-1] + f', "Participants": {users_data}' + "}"

    else:
        need_data = obj_to_dict(need)
        need_data = utf8_response(need_data)

    return need_data


class GetNeedById(Resource):
    @swag_from("./docs/need/id.yml")
    def get(self, need_id, confirm):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            if int(confirm) == 2:
                need = (
                    session.query(NeedModel)
                    .filter_by(isDeleted=False)
                    .filter_by(id=need_id)
                    .first()
                )
            elif int(confirm) == 1:
                need = (
                    session.query(NeedModel)
                    .filter_by(isDeleted=False)
                    .filter_by(id=need_id)
                    .filter_by(isConfirmed=True)
                    .first()
                )
            elif int(confirm) == 0:
                need = (
                    session.query(NeedModel)
                    .filter_by(isDeleted=False)
                    .filter_by(id=need_id)
                    .filter_by(isConfirmed=False)
                    .first()
                )
            else:
                return "{wrong input}"

            resp = Response(get_need(need, session))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetAllNeeds(Resource):
    @swag_from("./docs/need/all.yml")
    def get(self, confirm):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message1": "major error occurred!", "message2": str(datetime.now())}

        try:
            if int(confirm) == 2:
                needs = session.query(NeedModel).filter_by(isDeleted=False).all()
            elif int(confirm) == 1:
                needs = (
                    session.query(NeedModel)
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=True)
                    .all()
                )
            elif int(confirm) == 0:
                needs = (
                    session.query(NeedModel)
                    .filter_by(isDeleted=False)
                    .filter_by(isConfirmed=False)
                    .all()
                )
            else:
                return "{wrong input}"

            res = "{"
            for need in needs:
                res += f'"{str(need.id)}": {get_need(need, session)}, '

            resp = Response(res[:-2] + "}" if len(res) != 1 else "{}")

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetNeedByCategory(Resource):
    @swag_from("./docs/need/category.yml")
    def get(self, category):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            needs = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(category=category)
                .filter_by(isConfirmed=True)
                .all()
            )

            res = "{"
            for need in needs:
                res += f'"{str(need.id)}": {get_need(need, session)}, '

            resp = Response(res[:-2] + "}" if len(res) != 1 else "{}")

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetNeedByType(Resource):
    @swag_from("./docs/need/type.yml")
    def get(self, need_type):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            needs = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(type=need_type)
                .filter_by(isConfirmed=True)
                .all()
            )

            res = "{"
            for need in needs:
                res += f'"{str(need.id)}": {get_need(need, session)}, '

            resp = Response(res[:-2] + "}" if len(res) != 1 else "{}")

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetNeedParticipants(Resource):
    @swag_from("./docs/need/participants.yml")
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            resp = Response(get_need(need, session, participants_only=True))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetNeedReceipts(Resource):
    @swag_from("./docs/need/receipts.yml")
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            resp = Response(utf8_response({"NeedReceipts": need.receipts}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class GetAllUrgentNeeds(Resource):
    @swag_from("./docs/need/all_urgent.yml")
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            resp = Response(get_all_urgent_needs(session))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class AddPaymentForNeed(Resource):
    @swag_from("./docs/need/payment.yml")
    def post(self, need_id, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            amount = int(request.json["amount"])
            created_at = datetime.now()

            need = (
                session.query(NeedModel)
                .filter_by(isDeleted=False)
                .filter_by(id=need_id)
                .first()
            )

            if not need.isConfirmed:
                resp = Response(
                    json.dumps({"msg": "error: need is not confirmed yet!"})
                )
                session.close()
                return resp

            user = (
                session.query(UserModel)
                .filter_by(isDeleted=False)
                .filter_by(id=user_id)
                .first()
            )
            child = (
                session.query(ChildNeedModel)
                .filter_by(id_need=need_id)
                .filter_by(isDeleted=False)
                .first()
            )
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
                resp = Response(
                    json.dumps(
                        {"message": "payment must be added by the child's family!"}
                    )
                )
                session.close()
                return resp

            if amount > need.cost - need.paid:
                resp = Response(
                    json.dumps({"msg": f"you can pay {need.cost - need.paid} at most!"})
                )
                session.close()
                return resp

            elif amount > user.credit:
                resp = Response(
                    json.dumps(
                        {
                            "msg": f"your credit is less than {amount}! you have {user.credit}."
                        }
                    )
                )
                session.close()
                return resp

            elif amount <= 0:
                resp = Response(json.dumps({"msg": "amount can not be 0 or less!"}))
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
                need.progress = need.paid / need.cost * 100

                child.child_relation.spentCredit += amount
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
                        participate.user_relation.doneNeedCount += 1

                    child.child_relation.doneNeedCount += 1

                session.commit()

                resp = Response(json.dumps({"msg": "payment added successfully!"}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"msg": "ERROR OCCURRED!"}))

        finally:
            session.close()
            return resp


class UpdateNeedById(Resource):
    @swag_from("./docs/need/update.yml")
    def patch(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            primary_need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )
            child = (
                session.query(ChildNeedModel)
                .filter_by(id_need=need_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if "cost" in request.form.keys():
                if not primary_need.isConfirmed:
                    primary_need.cost = int(request.form["cost"])

                else:
                    resp = Response(
                        json.dumps(
                            {"msg": "error: cannot change cost for confirmed need!"}
                        )
                    )
                    session.close()
                    return resp

            if "imageUrl" in request.files.keys():
                file = request.files["imageUrl"]

                if file.filename == "":
                    resp = Response(
                        json.dumps({"message": "ERROR OCCURRED --> EMPTY FILE!"})
                    )
                    session.close()
                    return resp

                if file and allowed_image(file.filename):
                    # filename = secure_filename(file.filename)
                    filename = str(primary_need.id) + "." + file.filename.split(".")[-1]

                    temp_need_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(child.id_child) + "-child"
                    )
                    temp_need_path = os.path.join(temp_need_path, "needs")
                    temp_need_path = os.path.join(
                        temp_need_path, str(primary_need.id) + "-need"
                    )

                    for obj in os.listdir(temp_need_path):
                        check = str(primary_need.id) + "-image"

                        if obj.split("_")[0] == check:
                            os.remove(os.path.join(temp_need_path, obj))

                    primary_need.imageUrl = os.path.join(
                        temp_need_path, str(primary_need.id) + "-image_" + filename
                    )

                    file.save(primary_need.imageUrl)

                    resp = Response(json.dumps({"message": "WELL DONE!"}))

            if "receipts" in request.files.keys():
                file2 = request.files["receipts"]

                if file2.filename == "":
                    resp = Response(
                        json.dumps({"message": "ERROR OCCURRED --> EMPTY FILE!"})
                    )
                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    # filename = secure_filename(file2.filename)
                    if primary_need.receipts is not None:
                        filename = (
                            str(len(primary_need.receipts.split(",")))
                            + "."
                            + file2.filename.split(".")[-1]
                        )
                    else:
                        filename = str(0) + "." + file2.filename.split(".")[-1]

                    temp_need_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(child.id_child) + "-child"
                    )
                    temp_need_path = os.path.join(temp_need_path, "needs")
                    temp_need_path = os.path.join(
                        temp_need_path, str(primary_need.id) + "-need"
                    )
                    receipt_path = os.path.join(
                        temp_need_path, str(primary_need.id) + "-receipt_" + filename
                    )

                    if primary_need.receipts is None:
                        primary_need.receipts = str(receipt_path)

                    else:
                        primary_need.receipts += "," + str(receipt_path)

                    file2.save(receipt_path)

                    resp = Response(json.dumps({"message": "WELL DONE!"}))

            if "category" in request.form.keys():
                primary_need.category = int(request.form["category"])

            if "type" in request.form.keys():
                primary_need.type = int(request.form["type"])

            if "isUrgent" in request.form.keys():
                primary_need.isUrgent = (
                    True if request.form["isUrgent"] == "true" else False
                )

            if "affiliateLinkUrl" in request.form.keys():
                primary_need.affiliateLinkUrl = request.form["affiliateLinkUrl"]

            if "description" in request.form.keys():
                primary_need.description = request.form["description"]

            if "descriptionSummary" in request.form.keys():
                primary_need.descriptionSummary = request.form["descriptionSummary"]

            if "name" in request.form.keys():
                primary_need.name = request.form["name"]

            primary_need.lastUpdate = datetime.now()

            secondary_need = obj_to_dict(primary_need)

            session.commit()
            resp = Response(utf8_response(secondary_need))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"msg": "ERROR OCCURRED!"}))

        finally:
            session.close()
            return resp


class DeleteNeedById(Resource):
    @swag_from("./docs/need/delete.yml")
    def patch(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )
            families = (
                session.query(NeedFamilyModel)
                .filter_by(id_need=need_id)
                .filter_by(isDeleted=False)
                .all()
            )
            children = (
                session.query(ChildNeedModel)
                .filter_by(id_need=need_id)
                .filter_by(isDeleted=False)
                .all()
            )

            if need.isConfirmed:
                if need.paid != 0:
                    resp = Response(json.dumps({"msg": "error in deletion"}))
                    session.close()
                    return resp

            need.isDeleted = True

            for family in families:
                family.isDeleted = True

            for child in children:
                child.isDeleted = True
                child.child_relation.social_worker_relation.currentNeedCount -= 1

            session.commit()

            resp = Response(json.dumps({"msg": "need deleted successfully!"}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class ConfirmNeed(Resource):
    @swag_from("./docs/need/confirm.yml")
    def patch(self, need_id, social_worker_id, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            primary_need = (
                session.query(NeedModel)
                .filter_by(id=need_id)
                .filter_by(isDeleted=False)
                .first()
            )

            if primary_need.isConfirmed:
                resp = Response(
                    json.dumps({"message": "need has already been confirmed!"})
                )
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
            primary_need.confirmDate = datetime.now()

            new_child_need = ChildNeedModel(id_child=child_id, id_need=primary_need.id)

            if social_worker:
                social_worker.needCount += 1
                social_worker.currentNeedCount += 1

            session.add(new_child_need)
            session.commit()

            resp = Response(json.dumps({"message": "need confirmed successfully!"}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "ERROR OCCURRED"}))

        finally:
            session.close()
            return resp


class AddParticipantToNeed(Resource):
    @swag_from("./docs/need/add_participant.yml")
    def post(self, user_id, need_id, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            if (
                session.query(UserFamilyModel)
                .filter_by(isDeleted=False)
                .filter_by(id_family=family_id)
                .filter_by(id_user=user_id)
                .first()
                is None
            ):
                resp = Response(
                    json.dumps(
                        {"message": "participant must be from the child's family!"}
                    )
                )
                session.close()
                return resp

            new_participant = NeedFamilyModel(
                id_family=family_id, id_user=user_id, id_need=need_id
            )

            session.add(new_participant)
            session.commit()

            resp = Response(json.dumps({"msg": "participant added successfully!"}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({"message": "ERROR OCCURRED!"}))

        finally:
            session.close()
            return resp


class AddNeed(Resource):
    @swag_from("./docs/need/add.yml")
    def post(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {"message": "major error occurred!"}

        try:
            child = (
                session.query(ChildModel)
                .filter_by(id=child_id)
                .filter_by(isDeleted=False)
                .filter_by(isMigrated=False)
                .filter_by(isConfirmed=True)
                .first()
            )

            if not child.isConfirmed:
                resp = Response(
                    json.dumps({"message": "error: child is not confirmed yet!"})
                )
                session.close()
                return resp

            if len(session.query(NeedModel).all()):
                last_need = (
                    session.query(NeedModel).order_by(NeedModel.id.desc()).first()
                )
                current_id = last_need.id + 1

            else:
                current_id = 1

            image_path, receipt_path = None, None
            if "imageUrl" not in request.files:
                resp = Response(
                    json.dumps({"message": "ERROR OCCURRED IN FILE UPLOADING!"})
                )
                session.close()
                return resp

            file = request.files["imageUrl"]
            if file.filename == "":
                resp = Response(
                    json.dumps({"message": "ERROR OCCURRED --> EMPTY FILE!"})
                )
                session.close()
                return resp

            if file and allowed_image(file.filename):
                # filename = secure_filename(file.filename)
                filename = str(current_id) + "." + file.filename.split(".")[-1]

                temp_need_path = os.path.join(
                    app.config["UPLOAD_FOLDER"], str(child_id) + "-child"
                )
                temp_need_path = os.path.join(temp_need_path, "needs")
                temp_need_path = os.path.join(temp_need_path, str(current_id) + "-need")

                if not os.path.isdir(temp_need_path):
                    os.mkdir(temp_need_path)

                image_path = os.path.join(
                    temp_need_path, str(current_id) + "-image_" + filename
                )

                file.save(image_path)

                resp = Response(json.dumps({"message": "WELL DONE!"}))

            if "receipts" in request.files.keys():
                file2 = request.files["receipts"]
                if file2.filename == "":
                    resp = Response(
                        json.dumps({"message": "ERROR OCCURRED --> EMPTY FILE!"})
                    )
                    session.close()
                    return resp

                if file2 and allowed_image(file2.filename):
                    # filename = secure_filename(file2.filename)
                    filename = str(0) + "." + file2.filename.split(".")[-1]

                    temp_need_path = os.path.join(
                        app.config["UPLOAD_FOLDER"], str(child_id) + "-child"
                    )
                    temp_need_path = os.path.join(temp_need_path, "needs")
                    temp_need_path = os.path.join(
                        temp_need_path, str(current_id) + "-need"
                    )

                    if not os.path.isdir(temp_need_path):
                        os.mkdir(temp_need_path)

                    receipt_path = os.path.join(
                        temp_need_path, str(current_id) + "-receipt_" + filename
                    )

                    file2.save(receipt_path)

                    resp = Response(json.dumps({"message": "WELL DONE!"}))
            else:
                receipt_path = None

            image_url = image_path
            receipts = receipt_path

            category = int(request.form["category"])
            cost = request.form["cost"]
            name = request.form["name"]
            is_urgent = True if request.form["isUrgent"] == "true" else False
            need_type = request.form["type"]
            description = request.form["description"]
            description_summary = request.form["descriptionSummary"]

            created_at = datetime.now()
            last_update = datetime.now()

            if "affiliateLinkUrl" in request.form.keys():
                affiliate_link_url = request.form["affiliateLinkUrl"]
            else:
                affiliate_link_url = None

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
                receipts=receipts,
                type=need_type,
                lastUpdate=last_update,
            )

            session.add(new_need)
            session.commit()

            resp = Response(json.dumps({"message": "NEED ADDED SUCCESSFULLY!"}))

        except Exception as e:
            resp = Response(json.dumps({"message": "ERROR OCCURRED!"}))
            print(e)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetNeedById, "/api/v2/need/needId=<need_id>&confirm=<confirm>")
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
