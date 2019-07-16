from say.models.child_need_model import ChildNeedModel
from say.models.need_family_model import NeedFamilyModel
from say.models.need_model import NeedModel
from say.models.payment_model import PaymentModel
from say.models.user_model import UserModel
from . import *

"""
Need APIs
"""


def get_all_urgent_needs(session):
    needs = session.query(NeedModel).filter_by(IsUrgent=True).filter_by(IsDeleted=False).all()

    needs_data = {}
    for need in needs:
        needs_data[need.Id] = get_need(need, session)

    return needs_data


def get_need(need, session):
    child = session.query(ChildNeedModel).filter_by(Id_need=need.Id).filter_by(IsDeleted=False).first()
    participants = session.query(NeedFamilyModel).filter_by(Id_need=need.Id).filter_by(IsDeleted=False).all()

    need_data = obj_to_dict(need)
    child_data = obj_to_dict(child)

    users = {}
    for participant in participants:
        user = session.query(UserModel).filter_by(IsDeleted=False).get(participant.Id_user)
        users[user.Id] = obj_to_dict(user)

    need_data['ChildId'] = child_data
    need_data['Participants'] = users

    return need_data


class GetNeedById(Resource):
    @swag_from('./apidocs/need/id.yml')
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            need = session.query(NeedModel).filter_by(IsDeleted=False).filter_by(Id=need_id).first()

            need_data = get_need(need, session)

            resp = Response(json.dumps(need_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetNeedByCategory(Resource):
    @swag_from('./apidocs/need/category.yml')
    def get(self, category):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            needs = session.query(NeedModel).filter_by(IsDeleted=False).filter_by(Category=category).all()

            need_data = {}
            for need in needs:
                need_data[need.Id] = get_need(need, session)

            resp = Response(json.dumps(need_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetNeedByType(Resource):
    @swag_from('./apidocs/need/type.yml')
    def get(self, type):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            needs = session.query(NeedModel).filter_by(IsDeleted=False).filter_by(Type=type).all()

            need_data = {}
            for need in needs:
                need_data[need.Id] = get_need(need, session)

            resp = Response(json.dumps(need_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetNeedParticipants(Resource):
    @swag_from('./apidocs/need/participants.yml')
    def get(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            participants = session.query(NeedFamilyModel).filter_by(Id_need=need_id).filter_by(IsDeleted=False).all()
            need = session.query(NeedModel).filter_by(Id=need_id).filter_by(IsDeleted=False).first()

            users = {}
            for p in participants:
                user = session.query(UserModel).filter_by(IsDeleted=False).get(p.Id_user)
                users[user.Id] = obj_to_dict(user)

            users['TotalSpentCredit'] = need.Spent

            resp = Response(json.dumps(users))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllUrgentNeeds(Resource):
    @swag_from('./apidocs/need/urgents.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            needs_data = get_all_urgent_needs(session)

            resp = Response(json.dumps(needs_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class AddPaymentForNeed(Resource):
    @swag_from('./apidocs/need/payment.yml')
    def patch(self, need_id, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            Id_need = need_id
            Id_user = user_id
            Amount = int(request.form['Amount'])
            CreatedAt = datetime.now()

            user = session.query(UserModel).filter_by(IsDeleted=False).get(Id_user)
            need = session.query(NeedModel).filter_by(IsDeleted=False).get(Id_need)

            if Amount > need.Cost - need.Spent:
                resp = Response(json.dumps({'msg': 'error in payment!'}))
                session.close()
                return resp
            else:
                new_payment = PaymentModel(
                    Id_need=Id_need,
                    Id_user=Id_user,
                    Amount=Amount,
                    CreatedAt=CreatedAt,
                )

                session.add(new_payment)
                session.commit()

                user.Credit -= Amount
                need.Spent += Amount
                need.Progress = need.Spent // need.Cost

                if need.Spent == need.Cost:
                    need.Status = 2  # done

                session.commit()

                resp = Response(json.dumps({'msg': 'payment added successfully!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


class UpdateNeedById(Resource):
    @swag_from('./apidocs/need/update.yml')
    def patch(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            primary_need = session.query(NeedModel).filter_by(Id=need_id).filter_by(IsDeleted=False).first()

            if 'Cost' in request.form.keys():
                # if len(session.query(NeedFamilyModel).filter_by(Id_need=need_id).all()) != 0:
                if primary_need.IsConfirmed == 0:
                    primary_need.Cost = int(request.form['Cost'])
                else:
                    resp = Response(json.dumps({'msg': 'error in update need!'}))
                    session.close()
                    return resp
            if 'Description' in request.form.keys():
                primary_need.Description = request.form['Description']
            if 'DescriptionSummary' in request.form.keys():
                primary_need.DescriptionSummary = request.form['DescriptionSummary']
            if 'Name' in request.form.keys():
                primary_need.Name = request.form['Name']
            if 'ImageUrl' in request.files.keys():
                file = request.files['ImageUrl']
                if file.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                    session.close()
                    return resp
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    primary_need.ImageUrl = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(primary_need.ImageUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'Category' in request.form.keys():
                primary_need.Category = int(request.form['Category'])
            if 'Type' in request.form.keys():
                primary_need.Type = int(request.form['Type'])
            if 'IsUrgent' in request.form.keys():
                primary_need.IsUrgent = True if request.form['IsUrgent'] == 'true' else False
            if 'AffiliateLinkUrl' in request.form.keys():
                primary_need.AffiliateLinkUrl = request.form['AffiliateLinkUrl']
            if 'Receipts' in request.form.keys():
                if not primary_need.Receipt:
                    primary_need.Receipt += request.form['Receipts']
                else:
                    primary_need.Receipt = request.form['Receipts']

            primary_need.LastUpdate = datetime.now()

            secondary_need = obj_to_dict(primary_need)

            session.commit()
            resp = Response(json.dumps(secondary_need))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


class DeleteNeedById(Resource):
    @swag_from('./apidocs/need/delete.yml')
    def patch(self, need_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            need = session.query(NeedModel).filter_by(Id=need_id).filter_by(IsDeleted=False).first()
            families = session.query(NeedFamilyModel).filter_by(Id_need=need_id).filter_by(IsDeleted=False).all()
            children = session.query(ChildNeedModel).filter_by(Id_need=need_id).filter_by(IsDeleted=False).all()

            if need.IsConfirmed == 1:
                if need.Spent != 0:
                    resp = Response(json.dumps({'msg': 'error in deletion'}))
                    session.close()
                    return resp

            need.IsDeleted = 1

            for family in families:
                family.IsDeleted = 1

            for child in children:
                child.IsDeleted = 1

            session.commit()

            resp = Response(json.dumps({'msg': 'need deleted successfully!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class ConfirmNeed(Resource):
    @swag_from('./apidocs/need/confirm.yml')
    def patch(self, need_id, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            primary_need = session.query(NeedModel).filter_by(Id=need_id).filter_by(IsDeleted=False).first()
            # child = session.query(ChildNeedModel).filter_by(IsDeleted=False).get(need_id)

            if 'IsConfirmed' in request.form.keys():
                primary_need.IsConfirmed = request.form['IsConfirmed']
            if 'ConfirmUser' in request.form.keys():
                # if child.NgoId == request.form['NgoId']
                primary_need.ConfirmUser = user_id

            primary_need.ConfirmDate = datetime.now()

            secondary_need = obj_to_dict(primary_need)

            session.commit()
            resp = Response(json.dumps(secondary_need))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class AddParticipantToNeed(Resource):
    @swag_from('./apidocs/need/add_participant.yml')
    def patch(self, user_id, need_id, family_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            new_participant = NeedFamilyModel(
                Id_family=family_id,
                Id_user=user_id,
                Id_need=need_id
            )

            session.add(new_participant)
            session.commit()

            resp = Response(json.dumps({'msg': 'participant added successfully!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED!'}))

        finally:
            session.close()
            return resp


class AddNeed(Resource):
    @swag_from('./apidocs/need/add.yml')
    def post(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()
        resp = {'msg': 'shit happened.'}

        try:
            path = 'some wrong url'
            if 'Image' not in request.files:
                resp =  Response(json.dumps({'message': 'ERROR OCCURRED IN FILE UPLOADING!'}))
                session.close()
                return resp
            file = request.files['Image']
            if file.filename == '':
                resp =  Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                session.close()
                return resp
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                resp =  Response(json.dumps({'message': 'WELL DONE!'}))

            ImageUrl = path
            Name = request.form['Name']
            CreatedAt = datetime.now()
            Category = int(request.form['Category'])
            Cost = (request.form['Cost'])
            IsUrgent = True if request.form['IsUrgent'] == 'true' else False
            Type = (request.form['Type'])
            Description = request.form['Description']
            DescriptionSummary = request.form['DescriptionSummary']
            if 'AffiliateLinkUrl' in request.form.keys():
                AffiliateLinkUrl = request.form['AffiliateLinkUrl']
            else:
                AffiliateLinkUrl = None
            if 'Receipts' in request.form.keys():
                Receipts = request.form['Receipts']
            else:
                Receipts = None
            LastUpdate = datetime.now()
            # print(1)
            new_need = NeedModel(
                ImageUrl=ImageUrl,
                Name=Name,
                CreatedAt=CreatedAt,
                Category=Category,
                Cost=Cost,
                IsUrgent=IsUrgent,
                DescriptionSummary=DescriptionSummary,
                Description=Description,
                AffiliateLinkUrl=AffiliateLinkUrl,
                Receipts=Receipts,
                Type=Type,
                LastUpdate=LastUpdate
            )

            session.add(new_need)
            session.commit()

            new_child_need = ChildNeedModel(
                Id_child=child_id,
                Id_need=new_need.Id,
            )

            session.add(new_child_need)
            session.commit()

            resp = Response(json.dumps({'message': 'NEED ADDED SUCCESSFULLY!'}))

        except Exception as e:
            resp = Response(json.dumps({'message': 'ERROR OCCURRED!'}))
            print(e)

        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetNeedById, '/api/v2/need/needId=<need_id>')
api.add_resource(GetNeedByCategory, '/api/v2/need/category=<category>')
api.add_resource(GetNeedByType, '/api/v2/need/type=<type>')
api.add_resource(GetNeedParticipants, '/api/v2/need/participants/needId=<need_id>')
api.add_resource(GetAllUrgentNeeds, '/api/v2/need/urgent/all')
api.add_resource(AddPaymentForNeed, '/api/v2/need/payment/needId=<need_id>%userId=<user_id>')
api.add_resource(UpdateNeedById, '/api/v2/need/update/needId=<need_id>')
api.add_resource(DeleteNeedById, '/api/v2/need/delete/needId=<need_id>')
api.add_resource(ConfirmNeed, '/api/v2/need/confirm/needId=<need_id>')
api.add_resource(AddParticipantToNeed, '/api/v2/need/participants/add/needId=<need_id>%userId=<user_id>%familyId=<family_id>')
api.add_resource(AddNeed, '/api/v2/need/add/childId=<child_id>')
