from say.models.social_worker_model import SocialWorkerModel
from . import *

"""
Social Worker APIs
"""


class GetAllSocialWorkers(Resource):
    @swag_from('./apidocs/social_worker/all.yml')
    def get(self):
        Session = sessionmaker(db)
        session = Session()

        try:
            socialworkers = session.query(SocialWorkerModel).filter_by(IsActive=True).filter_by(IsDeleted=False).all()

            fetch = {}

            for socialworker in socialworkers:
                data = obj_to_dict(socialworker)
                fetch[socialworker.Id] = data

            resp = Response(json.dumps(fetch), status=200, headers={'Access-Control-Allow-Origin': '*'})
        except Exception as e:
            print(e)
        finally:
            session.close()
            return resp


class AddSocialWorker(Resource):
    @swag_from('./apidocs/social_worker/add.yml')
    def post(self):
        Session = sessionmaker(db)
        session = Session()

        try:
            id_card, passport, avatar = 'wrong id card', 'wrong passport', 'wrong avatar'
            if 'IdCardUrl' not in request.files or 'PassportUrl' not in request.files or 'AvatarUrl' not in request.files:
                resp = Response(json.dumps({'message': 'ERROR OCCURRED IN FILE UPLOADING!'}))
                session.close()
                return resp
            file1 = request.files['IdCardUrl']
            file2 = request.files['PassportUrl']
            file3 = request.files['AvatarUrl']
            if file1.filename == '':
                resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY ID CARD!'}))
                session.close()
                return resp
            if file2.filename == '':
                resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY PASSPORT!'}))
                session.close()
                return resp
            if file3.filename == '':
                resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY AVATAR!'}))
                session.close()
                return resp
            if file1 and allowed_file(file1.filename):
                filename = secure_filename(file1.filename)
                id_card = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file1.save(id_card)
                resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if file2 and allowed_file(file2.filename):
                filename = secure_filename(file2.filename)
                passport = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file2.save(passport)
                resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if file3 and allowed_file(file3.filename):
                filename = secure_filename(file3.filename)
                avatar = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file3.save(avatar)
                resp = Response(json.dumps({'message': 'WELL DONE!'}))

            lastObj = session.query(SocialWorkerModel).order_by(SocialWorkerModel.Id.desc()).first()
            currentId = lastObj.Id + 1

            Id_ngo = int(request.form['Id_ngo'])
            Country = int(request.form['Country'])
            City = int(request.form['City'])
            Id_type = int(request.form['Id_type'])
            FirstName = request.form['FirstName']
            LastName = request.form['LastName']
            UserName = request.form['UserName']
            Password = "SayPanel" + str(currentId)
            BirthCertificateNumber = request.form['BirthCertificateNumber']
            IdNumber = request.form['IdNumber']
            IdCardUrl = id_card
            PassportNumber = request.form['PassportNumber']
            PassportUrl = passport
            Gender = request.form['Gender']
            BirthDate = datetime.strptime(request.form['BirthDate'], '%Y-%m-%d')
            PhoneNumber = request.form['PhoneNumber']
            EmergencyPhoneNumber = request.form['EmergencyPhoneNumber']
            EmailAddress = request.form['EmailAddress']
            TelegramId = request.form['TelegramId']
            PostalAddress = request.form['PostalAddress']
            AvatarUrl = avatar
            BankAccountNumber = request.form['BankAccountNumber']
            BankAccountShebaNumber = request.form['BankAccountShebaNumber']
            BankAccountCardNumber = request.form['BankAccountCardNumber']
            RegisterDate = datetime.now()
            LastUpdateDate = datetime.now()
            LastLoginDate = datetime.now()
            GeneratedCode = str(Id_ngo) + str(currentId)

            new_socialWorker = SocialWorkerModel(
                Id_ngo=Id_ngo,
                Country=Country,
                City=City,
                Id_type=Id_type,
                FirstName=FirstName,
                LastName=LastName,
                UserName=UserName,
                Password=Password,
                BirthCertificateNumber=BirthCertificateNumber,
                IdNumber=IdNumber,
                IdCardUrl=IdCardUrl,
                PassportNumber=PassportNumber,
                PassportUrl=PassportUrl,
                Gender=Gender,
                BirthDate=BirthDate,
                PhoneNumber=PhoneNumber,
                EmergencyPhoneNumber=EmergencyPhoneNumber,
                EmailAddress=EmailAddress,
                TelegramId=TelegramId,
                PostalAddress=PostalAddress,
                AvatarUrl=AvatarUrl,
                BankAccountNumber=BankAccountNumber,
                BankAccountShebaNumber=BankAccountShebaNumber,
                BankAccountCardNumber=BankAccountCardNumber,
                RegisterDate=RegisterDate,
                LastUpdateDate=LastUpdateDate,
                LastLoginDate=LastLoginDate,
                GeneratedCode=GeneratedCode,
            )

            session.add(new_socialWorker)
            session.commit()

            res = {'msg': 'social_worker is created'}
            resp = Response(json.dumps(res), status=200, headers={'Access-Control-Allow-Origin': '*'})

        except Exception as e:
            print(e)
        finally:
            session.close()
            return resp


class GetSocialWorkerById(Resource):
    @swag_from('./apidocs/social_worker/id.yml')
    def get(self, socialworker_id):
        try:
            Session = sessionmaker(db)
            session = Session()

            socialworker = session.query(SocialWorkerModel).filter_by(Id=socialworker_id).filter_by(
                IsActive=True).filter_by(
                IsDeleted=False).first()
            if not socialworker:
                resp = Response(json.dumps({'message': 'error'}))
                session.close()
                return resp
            resp = Response(json.dumps(obj_to_dict(socialworker)), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByGeneratedCode(Resource):
    @swag_from('./apidocs/social_worker/gcode.yml')
    def get(self, socialworker_generatedcode):
        Session = sessionmaker(db)
        session = Session()

        try:
            socialworker = session.query(SocialWorkerModel).filter_by(
                GeneratedCode=socialworker_generatedcode).filter_by(
                IsActive=True).filter_by(IsDeleted=False).first()
            if not socialworker:
                resp = Response(json.dumps({'message': 'error'}))
                session.close()
                return resp
            resp = Response(json.dumps(obj_to_dict(socialworker)), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByNgoId(Resource):
    @swag_from('./apidocs/social_worker/ngo.yml')
    def get(self, socialworker_ngoid):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(Id_ngo=socialworker_ngoid).filter_by(
                IsActive=True).filter_by(IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByIdNumber(Resource):
    @swag_from('./apidocs/social_worker/idnumber.yml')
    def get(self, socialworker_idnumber):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(IdNumber=socialworker_idnumber).filter_by(
                isActive=True).filter_by(isDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByPhoneNumber(Resource):
    @swag_from('./apidocs/social_worker/phone.yml')
    def get(self, socialworker_phonenumber):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(PhoneNumber=socialworker_phonenumber).filter_by(
                IsActive=True).filter_by(IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByPassportNumber(Resource):
    @swag_from('./apidocs/social_worker/passport.yml')
    def get(self, socialworker_passportnumber):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(
                PassportNumber=socialworker_passportnumber).filter_by(
                IsActive=True).filter_by(IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.Id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByUserName(Resource):
    @swag_from('./apidocs/social_worker/username.yml')
    def get(self, socialworker_username):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(UserName=socialworker_username).filter_by(
                IsActive=True).filter_by(IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByBirthCertificateNumber(Resource):
    @swag_from('./apidocs/social_worker/bcnumber.yml')
    def get(self, socialworker_birthcertificatenumber):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(
                BirthCertificateNumber=socialworker_birthcertificatenumber).filter_by(IsActive=True).filter_by(
                IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByEmailAddress(Resource):
    @swag_from('./apidocs/social_worker/email.yml')
    def get(self, socialworker_emailaddress):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(
                EmailAddress=socialworker_emailaddress).filter_by(
                IsActive=True).filter_by(IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class GetSocialWorkerByTelegramId(Resource):
    @swag_from('./apidocs/social_worker/telegram.yml')
    def get(self, socialworker_telegramid):
        Session = sessionmaker(db)
        session = Session()

        try:
            fetch = {}

            socialworkers = session.query(SocialWorkerModel).filter_by(TelegramId=socialworker_telegramid).filter_by(
                IsActive=True).filter_by(IsDeleted=False).all()
            for socialworker in socialworkers:
                if not socialworker:
                    resp = Response(json.dumps({'message': 'error'}))
                    session.close()
                    return resp
                data = obj_to_dict(socialworker)

                fetch[socialworker.id] = data

            resp = Response(json.dumps(fetch), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class UpdateSocialWorker(Resource):
    @swag_from('./apidocs/social_worker/update.yml')
    def patch(self, socialworker_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_socialworker = session.query(SocialWorkerModel).filter_by(id=socialworker_id).filter_by(
                isActive=True).filter_by(isDeleted=False).first()

            if 'Id_ngo' in request.form.keys():
                base_socialworker.Id_ngo = int(request.form['Id_ngo'])
            if 'Country' in request.form.keys():
                base_socialworker.Country = int(request.form['Country'])
            if 'City' in request.form.keys():
                base_socialworker.City = int(request.form['City'])
            if 'Id_type' in request.form.keys():
                base_socialworker.Id_type = int(request.form['Id_type'])
            if 'FirstName' in request.form.keys():
                base_socialworker.FirstName = request.form['FirstName']
            if 'LastName' in request.form.keys():
                base_socialworker.LastName = request.form['LastName']
            if 'UserName' in request.form.keys():
                base_socialworker.UserName = request.form['UserName']
            if 'BirthCertificateNumber' in request.form.keys():
                base_socialworker.BirthCertificateNumber = request.form['BirthCertificateNumber']
            if 'IdNumber' in request.form.keys():
                base_socialworker.IdNumber = request.form['IdNumber']
            if 'IdCardUrl' in request.form.keys():
                file1 = request.files['VoiceUrl']
                if file1.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY VOICE!'}))
                    session.close()
                    return resp
                if file1 and allowed_file(file1.filename):
                    filename = secure_filename(file1.filename)
                    base_socialworker.IdCardUrl = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file1.save(base_socialworker.IdCardUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'PassportNumber' in request.form.keys():
                base_socialworker.PassportNumber = request.form['PassportNumber']
            if 'PassportUrl' in request.form.keys():
                file1 = request.files['VoiceUrl']
                if file1.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY VOICE!'}))
                    session.close()
                    return resp
                if file1 and allowed_file(file1.filename):
                    filename = secure_filename(file1.filename)
                    base_socialworker.PassportUrl = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file1.save(base_socialworker.PassportUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'Gender' in request.form.keys():
                base_socialworker.Gender = True if request.form['Gender'] =='true' else False
            if 'BirthDate' in request.form.keys():
                base_socialworker.BirthDate = datetime.strptime(request.form['BirthDate'], '%Y-%m-%d')
            if 'PhoneNumber' in request.form.keys():
                base_socialworker.PhoneNumber = request.form['PhoneNumber']
            if 'EmergencyPhoneNumber' in request.form.keys():
                base_socialworker.EmergencyPhoneNumber = request.form['EmergencyPhoneNumber']
            if 'EmailAddress' in request.form.keys():
                base_socialworker.EmailAddress = request.form['EmailAddress']
            if 'TelegramId' in request.form.keys():
                base_socialworker.TelegramId = request.form['TelegramId']
            if 'PostalAddress' in request.form.keys():
                base_socialworker.PostalAddress = request.form['PostalAddress']
            if 'AvatarUrl' in request.form.keys():
                file1 = request.files['VoiceUrl']
                if file1.filename == '':
                    resp = Response(json.dumps({'message': 'ERROR OCCURRED --> EMPTY VOICE!'}))
                    session.close()
                    return resp
                if file1 and allowed_file(file1.filename):
                    filename = secure_filename(file1.filename)
                    base_socialworker.AvatarUrl = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file1.save(base_socialworker.AvatarUrl)
                    resp = Response(json.dumps({'message': 'WELL DONE!'}))
            if 'BankAccountNumber' in request.form.keys():
                base_socialworker.BankAccountNumber = request.form['BankAccountNumber']
            if 'BankAccountShebaNumber' in request.form.keys():
                base_socialworker.BankAccountShebaNumber = request.form['BankAccountShebaNumber']
            if 'BankAccountCardNumber' in request.form.keys():
                base_socialworker.BankAccountCardNumber = request.form['BankAccountCardNumber']
            base_socialworker.LastUpdateDate = datetime.now()

            res = obj_to_dict(base_socialworker)

            resp = Response(json.dumps(res), status=200)
            session.commit()

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class DeleteSocialWorker(Resource):
    @swag_from('./apidocs/social_worker/delete.yml')
    def patch(self, socialworker_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_socialworker = session.query(SocialWorkerModel).filter_by(Id=socialworker_id).filter_by(
                IsActive=True).filter_by(IsDeleted=False).first()

            base_socialworker.IsDeleted = True

            # res = obj_to_dict(base_socialworker)

            session.commit()
            resp = Response(json.dumps({'msg': 'social worker deleted successfully!'}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


class DeactivateSocialWorker(Resource):
    @swag_from('./apidocs/social_worker/deactivate.yml')
    def patch(self, socialworker_id):
        Session = sessionmaker(db)
        session = Session()

        try:
            base_socialworker = session.query(SocialWorkerModel).filter_by(Id=socialworker_id).filter_by(
                IsActive=True).filter_by(IsDeleted=False).first()

            base_socialworker.IsActive = False

            # res = obj_to_dict(base_socialworker)

            session.commit()
            resp = Response(json.dumps({'msg': 'social worker deactivated successfully!'}), status=200)

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'message': 'error'}), status=500)
        finally:
            session.close()
            return resp


"""
API URLs
"""

api.add_resource(GetAllSocialWorkers, '/api/v2/socialWorker/all')
api.add_resource(AddSocialWorker, '/api/v2/socialWorker/add')
api.add_resource(GetSocialWorkerById, '/api/v2/socialWorker/socialWorkerId=<socialworker_id>')
api.add_resource(GetSocialWorkerByGeneratedCode, '/api/v2/socialWorker/generatedCode=<socialworker_generatedcode>')
api.add_resource(GetSocialWorkerByNgoId, '/api/v2/socialWorker/ngoId=<socialworker_ngoid>')
api.add_resource(GetSocialWorkerByIdNumber, '/api/v2/socialWorker/idNumber=<socialworker_idnumber>')
api.add_resource(GetSocialWorkerByPhoneNumber, '/api/v2/socialWorker/phone=<socialworker_phonenumber>')
api.add_resource(GetSocialWorkerByPassportNumber, '/api/v2/socialWorker/PassportName=<socialworker_passportnumber>')
api.add_resource(GetSocialWorkerByUserName, '/api/v2/socialWorker/username=<socialworker_username>')
api.add_resource(GetSocialWorkerByBirthCertificateNumber,
                 '/api/v2/socialWorker/bcNumber=<socialworker_birthcertificatenumber>')
api.add_resource(GetSocialWorkerByEmailAddress, '/api/v2/socialWorker/email=<socialworker_emailaddress>')
api.add_resource(GetSocialWorkerByTelegramId, '/api/v2/socialWorker/telegramId=<socialworker_telegramid>')
api.add_resource(UpdateSocialWorker, '/api/v2/socialWorker/update/socialWorkerId=<socialworker_id>')
api.add_resource(DeleteSocialWorker, '/api/v2/socialWorker/delete/socialWorkerId=<socialworker_id>')
api.add_resource(DeactivateSocialWorker, '/api/v2/socialWorker/deactivate/socialWorkerId=<socialworker_id>')
