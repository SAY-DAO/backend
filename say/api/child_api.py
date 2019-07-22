from flasgger.utils import validate

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
Child APIs
"""


def get_child_by_id(session, child_id):
    child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()
    needs = session.query(ChildNeedModel).filter_by(Id_child=child_id).filter_by(IsDeleted=False).all()
    print(111)
    print('$$$$$', child_id)

    child_data = obj_to_dict(child)
    print(222)

    child_needs = {}
    for need in needs:
        need_data = obj_to_dict(session.query(NeedModel).filter_by(Id=need.Id_need).filter_by(IsDeleted=False).first())
        print(333)
        child_needs[need.Id_need] = need_data

    child_data['Needs'] = child_needs

    return child_data


def get_child_need(session, child_id, urgent=False):
    needs = session.query(ChildNeedModel).filter_by(Id_child=child_id).filter_by(IsDeleted=False).all()

    child_needs = {}
    for need in needs:
        if not urgent:
            need_data = obj_to_dict(session.query(NeedModel).filter_by(Id=need.Id_need).filter_by(IsDeleted=False).first())
            child_needs['need'+str(need_data['Id'])] = need_data
        else:
            if need.need_relation.IsUrgent:
                need_data = obj_to_dict(session.query(NeedModel).filter_by(Id=need.Id_need).filter_by(IsDeleted=False).first())
                child_needs['need'+str(need['Id'])] = need_data

            if not len(child_needs):
                child_needs = {['msg']: 'no urgent needs founded!'}

    return child_needs


def generateCode(ngoId , swId , childId):
    res = ""
    ngo = "000"
    sw = "000"
    child = "0000"
    index = 2
    while ngoId > 0:
        ngo[index] = str(ngoId%10)
        ngoId = ngoId/10
        index = index - 1
    
    index = 2
    while swId > 0:
        sw[index] = str(swId%10)
        swId = swId/10
        index = index - 1
    
    index = 3
    while childId > 0:
        child[index] = str(childId%10)
        childId = childId/10
        index = index - 1
    
    res = ngo + sw + child
    print(res)
    return res


class GetAllChildren(Resource):
    @swag_from('./apidocs/child/all.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            children = session.query(ChildModel).filter_by().all()

            result = {}
            for child in children:

                needs = session.query(ChildNeedModel).filter_by(Id_child=child.Id).filter_by(IsDeleted=False).all()

                child_data = obj_to_dict(child)

                child_res = {}
                for need in needs:
                    need_data = obj_to_dict(need)
                    child_res[need.Id] = need_data

                child_data['Needs'] = child_res
                result[child.Id] = child_data

            resp = Response(json.dumps(result))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildById(Resource):
    @swag_from('./apidocs/child/id.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child_data = get_child_by_id(session, child_id)

            resp = Response(json.dumps(child_data))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildrenOfUserByUserId(Resource):
    @swag_from('./apidocs/child/user_children.yml')
    def get(self, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            users = session.query(UserFamilyModel).filter_by(Id_user=user_id).filter_by(IsDeleted=False).all()

            child_res = {}
            for user in users:
                families = session.query(FamilyModel).filter_by(Id=user.Id_family).filter_by(IsDeleted=False).all()

                for family in families:
                    child_data = get_child_by_id(session, family.family_child_relation.Id)
                    child_res[family.Id] = child_data

            resp = Response(json.dumps(child_res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildNeeds(Resource):
    @swag_from('./apidocs/child/needs.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            needs = session.query(ChildNeedModel).filter_by(Id_child=child_id).filter_by(IsDeleted=False).all()

            need_res = {}
            for need in needs:
                need_data = obj_to_dict(session.query(NeedModel).filter_by(Id=need.Id_need).filter_by(IsDeleted=False).first())
                need_res[need.Id] = need_data

            resp = Response(json.dumps(need_res))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildSayName(Resource):
    @swag_from('./apidocs/child/say_name.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            resp = Response(json.dumps({'ChildSayName': child.SayName}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildFamilyId(Resource):
    @swag_from('./apidocs/child/family_id.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            family = session.query(FamilyModel).filter_by(Id_child=child_id).filter_by(IsDeleted=False).first()

            resp = Response(json.dumps({'ChildFamilyId': family.Id}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildAvatarUrl(Resource):
    @swag_from('./apidocs/child/avatar.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            resp = Response(json.dumps({'ChildAvatarUrl': child.AvatarUrl}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildCreditSpent(Resource):
    @swag_from('./apidocs/child/spent.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            resp = Response(json.dumps({'ChildCreditSpent': child.SpentCredit}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class AddChild(Resource):
    @swag_from('./apidocs/child/add.yml')
    def post(self, social_worker_id, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            ngo = session.query(NgoModel).filter_by(Id=ngo_id).filter_by(IsDeleted=False).first()
            sw = session.query(SocialWorkerModel).filter_by(Id=social_worker_id).filter_by(IsDeleted=False).first()

            code = generateCode(ngo_id , social_worker_id , sw.childCount)
            # code = str(ngo_id) + str(social_worker_id) + str(sw.ChildCount)
            children = session.query(ChildModel).filter_by(IsDeleted=False).all()
            for child in children:
                if code == child.GeneratedCode:
                    resp = Response(json.dumps({'message': 'Child was already here!'}))
                    session.close()
                    return resp

            if len(session.query(ChildModel).all()):
                last_child = session.query(ChildModel).order_by(ChildModel.Id.desc()).first()
                current_id = last_child.Id + 1
            else:
                current_id = 1

            print(list(request.files.keys()))
            print(list(request.form.keys()))
            avatar_path, voice_path = 'wrong avatar', 'wrong voice'
            if 'VoiceUrl' not in request.files or 'AvatarUrl' not in request.files:
                resp = Response(json.dumps({'message': 'ERROR OCCURRED IN FILE UPLOADING!'}))
                session.close()
                return resp
            file1 = request.files['VoiceUrl']
            file2 = request.files['AvatarUrl']
            if file1.filename == '':
                resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY VOICE!'}))
                session.close()
                return resp
            if file2.filename == '':
                resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY AVATAR!'}))
                session.close()
                return resp
            if file1 and allowed_voice(file1.filename):
                filename = secure_filename(file1.filename)

                temp_voice_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-child')
                if not os.path.isdir(temp_voice_path):
                    os.mkdir(temp_voice_path)

                voice_path = os.path.join(temp_voice_path, str(current_id) + '-voice_' + filename)
                file1.save(voice_path)
                resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if file2 and allowed_image(file2.filename):
                filename = secure_filename(file2.filename)

                temp_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-child')
                if not os.path.isdir(temp_avatar_path):
                    os.mkdir(temp_avatar_path)
                temp_need_path = os.path.join(temp_avatar_path, 'needs')
                if not os.path.isdir(temp_need_path):
                    os.mkdir(temp_need_path)

                avatar_path = os.path.join(temp_avatar_path, str(current_id) + '-avatar_' + filename)
                file2.save(avatar_path)
                resp = Response(json.dumps({'message': 'WELL DONE!'}))

            if 'Nationality' in request.form.keys():
                Nationality = request.form['Nationality']
            else:
                Nationality = None
            if 'HousingStatus' in request.form.keys():
                HousingStatus = request.form['HousingStatus']
            else:
                HousingStatus = None
            if 'FirstName' in request.form.keys():
                FirstName = request.form['FirstName']
            else:
                FirstName = None
            if 'LastName' in request.form.keys():
                LastName = request.form['LastName']
            else:
                LastName = None
            if 'BirthPlace' in request.form.keys():
                BirthPlace = request.form['BirthPlace']
            else:
                BirthPlace = None
            if 'BirthDate' in request.form.keys():
                BirthDate = datetime.strptime(request.form['BirthDate'], '%Y-%m-%d')
            else:
                BirthDate = None
            if 'Address' in request.form.keys():
                Address = request.form['Address']
            else:
                Address = None
            if 'Status' in request.form.keys():
                Status = int(request.form['Status'])
            else:
                Status = None
            if 'Education' in request.form.keys():
                Education = request.form['Education']
            else:
                Education = None
            if 'FamilyCount' in request.form.keys():
                FamilyCount = int(request.form['FamilyCount'])
            else:
                FamilyCount = None
            PhoneNumber = request.form['PhoneNumber']
            AvatarUrl = avatar_path
            Bio = request.form['Bio']
            VoiceUrl = voice_path
            NgoId = ngo_id
            SocialWorkerId = social_worker_id
            SayName = request.form['SayName']
            Country = int(request.form['Country'])
            City = int(request.form['City'])
            Gender = True if request.form['Gender'] == 'true' else False
            BioSummary = request.form['BioSummary']
            CreatedAt = datetime.now()
            LastUpdate = datetime.now()


            new_child = ChildModel(
                PhoneNumber=PhoneNumber,
                Nationality=Nationality,
                AvatarUrl=AvatarUrl,
                HousingStatus=HousingStatus,
                FirstName=FirstName,
                LastName=LastName,
                FamilyCount=FamilyCount,
                Education=Education,
                CreatedAt=CreatedAt,
                BirthPlace=BirthPlace,
                BirthDate=BirthDate,
                Address=Address,
                Bio=Bio,
                VoiceUrl=VoiceUrl,
                NgoId=NgoId,
                SocialWorkerId=SocialWorkerId,
                SayName=SayName,
                Country=Country,
                City=City,
                Gender=Gender,
                BioSummary=BioSummary,
                Status=Status,
                LastUpdate=LastUpdate,
                GeneratedCode=code
            )

            session.add(new_child)
            session.commit()

            same_child = session.query(ChildModel).order_by(ChildModel.Id.desc()).filter_by(PhoneNumber=PhoneNumber).first()

            new_family = FamilyModel(
                Id_child=same_child.Id
            )

            ngo.ChildrenCount += 1
            sw.ChildCount += 1

            session.add(new_family)
            session.commit()

            resp = Response(json.dumps({'message': 'CHILD ADDED SUCCESSFULLY!'}))

        except Exception as e:
            resp = Response(json.dumps({'message': 'ERROR OCCURRED!'}))
            print(e)

        finally:
            session.close()
            return resp


class GetChildFamilyMembers(Resource):
    @swag_from('./apidocs/child/family.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            family = session.query(FamilyModel).filter_by(IsDeleted=False).filter_by(Id_child=child_id).first()
            members = session.query(UserFamilyModel).filter_by(Id_family=family.Id).filter_by(IsDeleted=False).all()

            family_res = {}
            for member in members:
                user = session.query(UserModel).filter_by(IsDeleted=False).filter_by(Id=member.Id_user).first()
                user_data = obj_to_dict(user)
                user_data['Role'] = member.UserRole
                family_res[user.Id] = user_data

            resp = Response(json.dumps(family_res))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class DeleteUserFromChildFamily(Resource):
    @swag_from('./apidocs/child/delete_member.yml')
    def patch(self, user_id, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            family = session.query(FamilyModel).filter_by(Id_child=child_id).filter_by(IsDeleted=False).first()
            user = session.query(UserFamilyModel).filter_by(Id_user=user_id).filter_by(Id_family=family.Id).filter_by(IsDeleted=False).first()
            participation = session.query(NeedFamilyModel).filter_by(Id_user=user_id).filter_by(Id_family=user_id).filter_by(IsDeleted=False).all()

            for participate in participation:
                participate.IsDeleted = True

            family.family_child_relation.SayFamilyCount -= 1
            user.IsDeleted = True
            if family.family_child_relation.SayFamilyCount == 0:
                family.family_child_relation.HasFamily = False

                # session.delete(user)
            session.commit()

            resp = Response(json.dumps({'msg': 'DELETED SUCCESSFULLY!'}))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class UpdateChildById(Resource):
    @swag_from('./apidocs/child/update.yml')
    def patch(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            primary_child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            if 'PhoneNumber' in request.form.keys():
                primary_child.PhoneNumber = request.form['PhoneNumber']
            if 'Nationality' in request.form.keys():
                primary_child.Nationality = request.form['Nationality']
            if 'AvatarUrl' in request.files.keys():
                file2 = request.files['AvatarUrl']
                if file2.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY AVATAR!'}))
                    session.close()
                    return resp
                if file2 and allowed_image(file2.filename):
                    filename = secure_filename(file2.filename)
                    temp_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], str(primary_child.Id) + '-child')
                    for obj in os.listdir(temp_avatar_path):
                        check = str(primary_child.Id) + '-avatar'
                        if obj.split('_')[0] == check:
                            os.remove(os.path.join(temp_avatar_path, obj))
                    primary_child.AvatarUrl =  os.path.join(temp_avatar_path, str(primary_child.Id) + '-avatar_' + filename)
                    file2.save(primary_child.AvatarUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'HousingStatus' in request.form.keys():
                primary_child.HousingStatus = request.form['HousingStatus']
            if 'FirstName' in request.form.keys():
                primary_child.FirstName = request.form['FirstName']
            if 'LastName' in request.form.keys():
                primary_child.LastName = request.form['LastName']
            if 'Gender' in request.form.keys():
                primary_child.Gender = True if request.form['Gender'] == 'true' else False
            if 'FamilyCount' in request.form.keys():
                primary_child.FamilyCount = int(request.form['FamilyCount'])
            if 'Country' in request.form.keys():
                primary_child.Country = int(request.form['Country'])
            if 'City' in request.form.keys():
                primary_child.City = int(request.form['City'])
            if 'Status' in request.form.keys():
                primary_child.Status = int(request.form['Status'])
            if 'Education' in request.form.keys():
                primary_child.Education = request.form['Education']
            if 'BirthPlace' in request.form.keys():
                primary_child.BirthPlace = request.form['BirthPlace']
            if 'BirthDate' in request.form.keys():
                primary_child.BirthDate = datetime.strptime(request.form['BirthDate'], '%Y-%m-%d')
            if 'Address' in request.form.keys():
                primary_child.Address = request.form['Address']
            if 'Bio' in request.form.keys():
                primary_child.Bio = request.form['Bio']
            if 'BioSummary' in request.form.keys():
                primary_child.BioSummary = request.form['BioSummary']
            if 'VoiceUrl' in request.form.keys():
                file1 = request.files['VoiceUrl']
                if file1.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY VOICE!'}))
                    session.close()
                    return resp
                if file1 and allowed_voice(file1.filename):
                    filename = secure_filename(file1.filename)
                    temp_voice_path = os.path.join(app.config['UPLOAD_FOLDER'], str(primary_child.Id) + '-child')
                    for obj in os.listdir(temp_voice_path):
                        check = str(primary_child.Id) + '-voice'
                        if obj.split('_')[0] == check:
                            os.remove(os.path.join(temp_voice_path, obj))
                    primary_child.VoiceUrl = os.path.join(temp_voice_path, str(primary_child.Id) + '-voice_' + filename)
                    file1.save(primary_child.VoiceUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'SayName' in request.form.keys():
                primary_child.SayName = request.form['SayName']

            primary_child.LastUpdate = datetime.now()

            secondary_child = obj_to_dict(primary_child)

            session.commit()
            resp = Response(json.dumps(secondary_child))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR IN UPDATECHILDBYID!'}))

        finally:
            session.close()
            return resp


class DeleteChildById(Resource):
    @swag_from('./apidocs/child/delete.yml')
    def patch(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            if not child.IsConfirmed:
                family = session.query(FamilyModel).filter_by(IsDeleted=False).filter_by(Id_child=child_id).first()

                child.IsDeleted = True
                family.IsDeleted = True

                session.commit()

                resp = Response(json.dumps({'msg': 'child deleted successfully!'}))
            else:
                resp = Response(json.dumps({'msg': 'error in deleting child!'}))
        # needs = session.query(ChildNeedModel).filter_by(Id_child=child_id).all()
        #
        # for need in needs:
        #     need.IsDeleted = 1
        #

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'ERROR IN DELETECHILDBYID!'}))

        finally:
            session.close()
            return resp


class GetChildrenByBirthPlace(Resource):
    @swag_from('./apidocs/child/birthplace.yml')
    def get(self, birth_place):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            children = session.query(ChildModel).filter_by(BirthPlace=birth_place).filter_by(IsDeleted=False).all()

            res = {}
            for child in children:
                child_data = obj_to_dict(child)
                res[child.Id] = child_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildrenByBirthDate(Resource):
    @swag_from('./apidocs/child/birthdate.yml')
    def get(self, birth_date, is_after):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            if is_after.lower() == 'true':
                children = session.query(ChildModel).filter(ChildModel.BirthDate >= birth_date).filter_by(
                    IsDeleted=False).all()
            else:
                children = session.query(ChildModel).filter(ChildModel.BirthDate <= birth_date).filter_by(
                    IsDeleted=False).all()

            res = {}
            for child in children:
                child_data = obj_to_dict(child)
                res[child.Id] = child_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildrenByNationality(Resource):
    @swag_from('./apidocs/child/nationality.yml')
    def get(self, nationality):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            children = session.query(ChildModel).filter_by(Nationality=nationality).filter_by(IsDeleted=False).all()

            res = {}
            for child in children:
                child_data = obj_to_dict(child)
                res[child.Id] = child_data

            resp = Response(json.dumps(res))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildByNgoId(Resource):
    @swag_from('./apidocs/child/ngo.yml')
    def get(self, ngo_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(NgoId=ngo_id).filter_by(IsDeleted=False).first()

            resp = Response(json.dumps(obj_to_dict(child)))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildBySocialWorkerId(Resource):
    @swag_from('./apidocs/child/socialworker.yml')
    def get(self, social_worker_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(SocialWorkerId=social_worker_id).filter_by(
                IsDeleted=False).first()

            resp = Response(json.dumps(obj_to_dict(child)))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildUrgentNeedsById(Resource):
    @swag_from('./apidocs/child/urgent.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            needs = session.query(ChildNeedModel).filter_by(Id_child=child_id).filter_by(IsDeleted=False).all()

            need_res = {}
            for need in needs:
                temps = session.query(NeedModel).filter_by(Id=need.Id_need).filter_by(IsDeleted=False).filter_by(
                    IsUrgent=True).all()
                for temp in temps:
                    need_data = obj_to_dict(temp)
                    need_res[need_data['Id']] = need_data

            resp = Response(json.dumps(need_res))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetAllChildrenUrgentNeeds(Resource):
    @swag_from('./apidocs/child/urgents.yml')
    def get(self):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            needs = session.query(ChildNeedModel).filter_by(IsDeleted=False).all()

            need_res = {}
            for need in needs:
                temps = session.query(NeedModel).filter_by(Id=need.Id_need).filter_by(IsDeleted=False).filter_by(IsUrgent=True).all()
                for temp in temps:
                    need_data = obj_to_dict(temp)
                    need_res[need_data['Id']] = need_data

            resp = Response(json.dumps(need_res))

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class ConfirmChild(Resource):
    @swag_from('./apidocs/child/confirm.yml')
    def patch(self, child_id, user_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            primary_child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            if 'IsConfirmed' in request.form.keys():
                primary_child.IsConfirmed = True if request.form['IsConfirmed'] == 'true' else False
            # if 'ConfirmUser' in request.form.keys():
            primary_child.ConfirmUser = user_id

            primary_child.ConfirmDate = datetime.now()

            session.commit()

            secondary_child = obj_to_dict(primary_child)

            resp = Response(json.dumps(secondary_child))


        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


class GetChildGeneratedCode(Resource):
    @swag_from('./apidocs/child/code.yml')
    def get(self, child_id):
        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            child = session.query(ChildModel).filter_by(Id=child_id).filter_by(IsDeleted=False).first()

            resp = Response(json.dumps({'ChildGeneratedCode': child.GeneratedCode}))

        except Exception as e:
            print(e)

            resp = Response(json.dumps({'message': 'ERROR OCCURRED'}))

        finally:
            session.close()
            return resp


"""
API URLs 
"""

api.add_resource(GetChildById, '/api/v2/child/childId=<child_id>')
api.add_resource(GetChildrenOfUserByUserId, '/api/v2/child/user/userId=<user_id>')
api.add_resource(GetAllChildren, '/api/v2/child/all')
api.add_resource(GetChildNeeds, '/api/v2/child/need/childId=<child_id>')
api.add_resource(GetChildSayName, '/api/v2/child/sayName/childId=<child_id>')
api.add_resource(GetChildFamilyId, '/api/v2/child/family/childId=<child_id>')
api.add_resource(GetChildAvatarUrl, '/api/v2/child/avatar/childId=<child_id>')
api.add_resource(GetChildCreditSpent, '/api/v2/child/creditSpent/childId=<child_id>')
api.add_resource(AddChild, '/api/v2/child/add/socialWorkerId=<social_worker_id>&ngoId=<ngo_id>')
api.add_resource(GetChildFamilyMembers, '/api/v2/child/family/members/childId=<child_id>')
api.add_resource(DeleteUserFromChildFamily, '/api/v2/child/family/delete/userId=<user_id>&childId=<child_id>')
api.add_resource(UpdateChildById, '/api/v2/child/update/childId=<child_id>')
api.add_resource(DeleteChildById, '/api/v2/child/delete/childId=<child_id>')
api.add_resource(GetChildrenByBirthPlace, '/api/v2/child/birthPlace=<birth_place>')
api.add_resource(GetChildrenByBirthDate, '/api/v2/child/date=<birth_date>&isAfter=<is_after>')
api.add_resource(GetChildrenByNationality, '/api/v2/child/nationality=<nationality>')
api.add_resource(GetChildByNgoId, '/api/v2/child/ngoId=<ngo_id>')
api.add_resource(GetChildBySocialWorkerId, '/api/v2/child/socialWorkerId=<social_worker_id>')
api.add_resource(GetChildUrgentNeedsById, '/api/v2/child/need/urgent/childId=<child_id>')
api.add_resource(GetAllChildrenUrgentNeeds, '/api/v2/child/need/urgent/all')
api.add_resource(ConfirmChild, '/api/v2/child/confirm/childId=<child_id>&userId=<user_id>')
api.add_resource(GetChildGeneratedCode, '/api/v2/child/generatedCode/childId=<child_id>')
