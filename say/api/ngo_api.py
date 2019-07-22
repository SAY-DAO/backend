from say.models.ngo_model import NgoModel
from . import *

"""
Activity APIs
"""


class GetAllNgo(Resource):
    @swag_from('./apidocs/ngo/all.yml')
    def get(self):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_ngos = session.query(NgoModel).filter_by(IsDeleted=False).all()

            fetch = {}

            for n in base_ngos:
                data = obj_to_dict(n)
                fetch[n.Id] = data
            print(fetch)
            resp = Response(json.dumps(fetch), status=200)
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}))
        finally:
            session.close()
            return resp


class AddNgo(Resource):
    @swag_from('./apidocs/ngo/add.yml')
    def post(self):
        Session = sessionmaker(db)
        session = Session()

        try:
            if len(session.query(NgoModel).all()):
                last_ngo = session.query(NgoModel).order_by(NgoModel.Id.desc()).first()
                current_id = last_ngo.Id + 1
            else:
                current_id = 1

            path = 'some wrong url'
            if 'LogoUrl' not in request.files:
                resp = Response(json.dumps({'message': 'ERROR OCCURRED IN FILE UPLOADING!'}))
                session.close()
                return resp
            file = request.files['LogoUrl']
            if file.filename == '':
                resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                session.close()
                return resp
            if file and allowed_image(file.filename):
                filename = secure_filename(file.filename)

                temp_logo_path = os.path.join(app.config['UPLOAD_FOLDER'], str(current_id) + '-ngo')
                if not os.path.isdir(temp_logo_path):
                    os.mkdir(temp_logo_path)

                path = os.path.join(temp_logo_path, str(current_id) + '-logo_' + filename)
                file.save(path)
                resp =  Response(json.dumps({'message': 'WELL DONE!'}))

            Country = int(request.form['Country'])
            City = int(request.form['City'])
            CoordinatorId = int(request.form['CoordinatorId'])
            Name = request.form['Name']
            PostalAddress = request.form['PostalAddress']
            EmailAddress = request.form['EmailAddress']
            PhoneNumber = request.form['PhoneNumber']
            LogoUrl = path
            Balance = int(request.form['Balance'])
            RegisterDate = datetime.now()
            LastUpdateDate = datetime.now()

            new_ngo = NgoModel(
                Name=Name,
                Country=Country,
                City=City,
                CoordinatorId=CoordinatorId,
                PostalAddress=PostalAddress,
                EmailAddress=EmailAddress,
                PhoneNumber=PhoneNumber,
                LogoUrl=LogoUrl,
                Balance=Balance,
                RegisterDate=RegisterDate,
                LastUpdateDate=LastUpdateDate,
            )

            session.add(new_ngo)
            session.commit()

            res = {'msg': 'ngo is created'}
            resp = Response(json.dumps(res), status=200, headers={'Access-Control-Allow-Origin': '*'})

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}))

        finally:
            session.close()
            return resp


class GetNgoById(Resource):
    @swag_from('./apidocs/ngo/id.yml')
    def get(self, ngo_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_ngo = session.query(NgoModel).filter_by(Id=ngo_id).filter_by(
                IsDeleted=False).first()

            if not base_ngo:
                resp = Response(json.dumps({'msg': 'sth went wrong!'}))
                session.close()
                return resp

            resp = Response(json.dumps(obj_to_dict(base_ngo)), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}))

        finally:
            session.close()
            return resp


class GetNgoByCoordinatorId(Resource):
    @swag_from('./apidocs/ngo/coordinator.yml')
    def get(self, ngo_coordinatorid):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            base_ngos = session.query(NgoModel).filter_by(CoordinatorId=ngo_coordinatorid).filter_by(IsDeleted=False).all()

            for n in base_ngos:
                if not n:
                    resp = Response(json.dumps({'msg': 'sth went wrong!'}))
                    session.close()
                    return resp

                data = obj_to_dict(n)

                fetch[n.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)

        finally:
            session.close()
            return resp


class GetNgoByName(Resource):
    @swag_from('./apidocs/ngo/name.yml')
    def get(self, ngo_name):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            base_ngos = session.query(NgoModel).filter_by(Name=ngo_name).filter_by(
                IsDeleted=False).all()

            for n in base_ngos:
                if not n:
                    resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)
                    session.close()
                    return resp

                data = obj_to_dict(n)

                fetch[n.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)

        finally:
            session.close()
            return resp


class GetNgoByPhoneNumber(Resource):
    @swag_from('./apidocs/ngo/phone.yml')
    def get(self, ngo_phonenumber):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            base_ngos = session.query(NgoModel).filter_by(PhoneNumber=ngo_phonenumber).filter_by(
                IsDeleted=False).all()

            for n in base_ngos:
                if not n:
                    resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)
                    session.close()
                    return resp

                data = obj_to_dict(n)

                fetch[n.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)

        finally:
            session.close()
            return resp


class UpdateNgo(Resource):
    @swag_from('./apidocs/ngo/update.yml')
    def patch(self, ngo_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_ngo = session.query(NgoModel).filter_by(Id=ngo_id).filter_by(
                IsDeleted=False).first()

            if 'Country' in request.form.keys():
                base_ngo.Country = int(request.form['Country'])
            if 'City' in request.form.keys():
                base_ngo.City = int(request.form['City'])
            if 'CoordinatorId' in request.form.keys():
                base_ngo.CoordinatorId = int(request.form['CoordinatorId'])
            if 'Name' in request.form.keys():
                base_ngo.Name = request.form['Name']
            if 'PostalAddress' in request.form.keys():
                base_ngo.PostalAddress = request.form['PostalAddress']
            if 'EmailAddress' in request.form.keys():
                base_ngo.EmailAddress = request.form['EmailAddress']
            if 'PhoneNumber' in request.form.keys():
                base_ngo.PhoneNumber = request.form['PhoneNumber']
            if 'LogoUrl' in request.files.keys():
                file = request.files['LogoUrl']
                if file.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY FILE!'}))
                    session.close()
                    return resp
                if file and allowed_image(file.filename):
                    filename = secure_filename(file.filename)
                    temp_logo_path = os.path.join(app.config['UPLOAD_FOLDER'], str(base_ngo.Id) + '-ngo')
                    for obj in os.listdir(temp_logo_path):
                        check = str(base_ngo.Id) + '-logo'
                        if obj.split('_')[0] == check:
                            os.remove(os.path.join(temp_logo_path, obj))
                    base_ngo.LogoUrl = os.path.join(temp_logo_path, str(base_ngo.Id) + '-logo_' + filename)
                    file.save(base_ngo.LogoUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'Balance' in request.form.keys():
                base_ngo.Balance = request.form['Balance']
            base_ngo.lastUpdateDate = datetime.now()

            res = obj_to_dict(base_ngo)

            resp = Response(json.dumps(res), status=200)
            session.commit()

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class DeleteNgo(Resource):
    @swag_from('./apidocs/ngo/delete.yml')
    def patch(self, ngo_id):
        Session = sessionmaker(db)
        session = Session()

        try:

            base_ngo = session.query(NgoModel).filter_by(Id=ngo_id).filter_by(
                IsDeleted=False).first()

            base_ngo.IsDeleted = True

            # res = obj_to_dict(base_ngo)

            session.commit()
            resp = Response(json.dumps({'msg': 'ngo deleted successfully!'}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class DeactivateNgo(Resource):
    @swag_from('./apidocs/ngo/deactivate.yml')
    def patch(self, ngo_id):
        Session = sessionmaker(db)
        session = Session()

        try:

            base_ngo = session.query(NgoModel).filter_by(Id=ngo_id).filter_by(IsActive=True).filter_by(
                IsDeleted=False).first()

            base_ngo.IsActive = False

            # res = obj_to_dict(base_ngo)

            session.commit()
            resp = Response(json.dumps({'msg': 'ngo deactivated successfully!'}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetAllNgo, '/api/v2/ngo/all')
api.add_resource(AddNgo, '/api/v2/ngo/add')
api.add_resource(GetNgoById, '/api/v2/ngo/ngoId=<ngo_id>')
api.add_resource(GetNgoByCoordinatorId, '/api/v2/ngo/coordinatorId=<ngo_coordinatorid>')
api.add_resource(GetNgoByName, '/api/v2/ngo/name=<ngo_name>')
api.add_resource(GetNgoByPhoneNumber, '/api/v2/ngo/phone=<ngo_phonenumber>')
api.add_resource(UpdateNgo, '/api/v2/ngo/update/ngoId=<ngo_id>')
api.add_resource(DeleteNgo, '/api/v2/ngo/delete/ngoId=<ngo_id>')
api.add_resource(DeactivateNgo, '/api/v2/ngo/deactivate/ngoId=<ngo_id>')
