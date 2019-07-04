import os
from say.models import socialWorker
from say.config import db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from flask import Flask, Blueprint, json, Response, request, abort
from werkzeug.utils import secure_filename
import requests
import datetime

current_time = datetime.datetime.now()
socialworker_avatar_folder = '../panel/assets/images/avatars/social_worker'
socialworker_idcard_folder = '../panel/assets/images/idcard/social_worker'
socialworker_passport_folder = '../panel/assets/images/passport/social_worker'
allowed_extensions = set(['jpd'])


socialworker = Blueprint('socialworker', __name__)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions




@socialworker.route('/socialworker', methods = ['GET', 'POST'])
def api_socialworker():

    if request.method == 'GET':
        # get all social workers

        try:
            Session =  sessionmaker(db)
            session = Session()

            socialworkers = session.query(socialWorker).filter_by(isActive = True).filter_by(isDeleted = False).all()
            
            fetch = {}

            for socialworker in socialworkers:

                data = object_as_dict(socialworker) 
                fetch[socialworker.id] = data

            resp = Response(json.dumps(fetch), status=200, headers={'Access-Control-Allow-Origin': '*'})
        except Exception as e:
            print(e)
        finally:
            session.close()
            return resp


    elif request.method == 'POST':
        # insert social worker

        try:
            Session =  sessionmaker(db)
            session = Session()

            lastObj = session.query(socialWorker).order_by(socialWorker.id.desc()).first()
            currentId = lastObj.id + 1
            # print(currentId)
            
            firstName = request.form['firstName']
            lastName = request.form['lastName']
            userName = request.form['userName']
            password = "SayPanel" + str(currentId)
            typeId = int(request.form['typeId'])
            ngoId = int(request.form['ngoId'])
            birthCertificateNumber = request.form['birthCertificateNumber']
            city = int(request.form['city'])
            country = int(request.form['country'])
            idNumber = request.form['idNumber']
            idCardUrl = request.form['idCardUrl']

            # check if the post request has the file part

            # if 'file' not in request.files:
            #     flash('No file part')
            #     return redirect(request.url)
            # idCardUrl = request.files['idCardUrl']

            # if user does not select file, browser also
            # submit an empty part without filename

            # if idCardUrl.filename == '':
            #     flash('No selected file')
            #     return redirect(request.url)
            # if idCardUrl and allowed_file(idCardUrl.filename):
            #     filename = secure_filename(idCardUrl.filename)
            #     id.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #     return redirect(url_for('uploaded_file',
            #                             filename=filename))


            passportNumber = request.form['passportNumber']
            passportUrl = request.form['passportUrl']
            gender = int(request.form['gender'])
            birthDate = datetime.datetime.strptime(request.form['birthDate'], '%Y-%m-%d')
            phoneNumber = request.form['phoneNumber']
            emergencyPhoneNumber = request.form['emergencyPhoneNumber']
            emailAddress = request.form['emailAddress']
            telegramId = request.form['telegramId']
            postalAddress = request.form['postalAddress']
            avatarUrl = request.form['avatarUrl']
            childCount = '0'
            needCount = '0'
            bankAccountNumber = request.form['bankAccountNumber']
            bankAccountShebaNumber = request.form['bankAccountShebaNumber']
            bankAccountCardNumber = request.form['bankAccountCardNumber']
            registerDate = current_time
            lastLoginDate = current_time
            lastUpdateDate = current_time
            lastLogoutDate = current_time
            isActive = 1
            isDeleted = 0
            generatedCode = str(ngoId) + str(currentId)


            # print(generatedCode)
            # print(password)

            new_socialWorker = socialWorker(
                generatedCode = generatedCode,
                ngo_id = ngoId,
                country_id = country,
                city_id = city,
                type_id = typeId,
                firstName = firstName,
                lastName = lastName,
                userName = userName,
                password = password,
                birthCertificateNumber = birthCertificateNumber,
                idNumber = idNumber,
                idCardUrl = idCardUrl,
                passportNumber = passportNumber,
                passportUrl = passportUrl,
                gender = gender,
                birthDate = birthDate,
                phoneNumber = phoneNumber,
                emergencyPhoneNumber = emergencyPhoneNumber,
                emailAddress = emailAddress,
                telegramId = telegramId,
                postalAddress = postalAddress,
                avatarUrl = avatarUrl,
                childCount = childCount,
                needCount = needCount,
                bankAccountNumber = bankAccountNumber,
                bankAccountShebaNumber = bankAccountShebaNumber,
                bankAccountCardNumber = bankAccountCardNumber,
                registerDate = registerDate,
                lastLoginDate = lastLoginDate,
                lastLogoutDate = lastLogoutDate,
                lastUpdateDate = lastUpdateDate,
                isActive = isActive,
                isDeleted = isDeleted
            )

            session.add(new_socialWorker)
            session.commit() 

            res = {'msg' : 'social_worker is created'}
            resp = Response(json.dumps(res) , status=200, headers={'Access-Control-Allow-Origin': '*'})           

        except Exception as e:
            print(e)
        finally:
            session.close()
            return resp




@socialworker.route('/socialworker/id/<int:socialworker_id>', methods = ['GET'])
def get_socialworkerById(socialworker_id):

    # get social worker by id
    try:
        Session =  sessionmaker(db)
        session = Session()

        socialworker = session.query(socialWorker).filter_by(id = socialworker_id).filter_by(isActive = True).filter_by(isDeleted = False).first()
        # print(object_as_dict(socialworker))
        if not socialworker:
            abort(400)
        resp = Response(json.dumps(object_as_dict(socialworker)) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/generatedcode/<socialworker_generatedcode>', methods = ['GET'])
def get_socialworkerByGeneratedCode(socialworker_generatedcode):

    # get social worker by generated code
    try:
        Session =  sessionmaker(db)
        session = Session()

        socialworker = session.query(socialWorker).filter_by(generatedCode = socialworker_generatedcode).filter_by(isActive = True).filter_by(isDeleted = False).first()
        # print(object_as_dict(socialworker))
        if not socialworker:
            abort(400)
        resp = Response(json.dumps(object_as_dict(socialworker)) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/ngoid/<int:socialworker_ngoid>', methods = ['GET'])
def get_socialworkerByNgoId(socialworker_ngoid):

    # get social worker by NGO Id
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(ngo_id = socialworker_ngoid).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/idnumber/<socialworker_idnumber>', methods = ['GET'])
def get_socialworkerByIdNumber(socialworker_idnumber):

    # get social worker by IdNumber
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(idNumber = socialworker_idnumber).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/phonenumber/<socialworker_phonenumber>', methods = ['GET'])
def get_socialworkerByPhoneNumber(socialworker_phonenumber):

    # get social worker by phone number
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(phoneNumber = socialworker_phonenumber).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp




@socialworker.route('/socialworker/passportnumber/<socialworker_passportnumber>', methods = ['GET'])
def get_socialworkerByPassportNumber(socialworker_passportnumber):

    # get social worker by passport number
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(passportNumber = socialworker_passportnumber).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp





@socialworker.route('/socialworker/username/<socialworker_username>', methods = ['GET'])
def get_socialworkerByUserName(socialworker_username):

    # get social worker by userName
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(userName = socialworker_username).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/birthcertificatenumber/<socialworker_birthcertificatenumber>', methods = ['GET'])
def get_socialworkerByBirthCertificateNumber(socialworker_birthcertificatenumber):

    # get social worker by birth certificate number
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(birthCertificateNumber = socialworker_birthcertificatenumber).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp





@socialworker.route('/socialworker/emailaddress/<socialworker_emailaddress>', methods = ['GET'])
def get_socialworkerByEmailAddress(socialworker_emailaddress):

    # get social worker by email address
    try:
        Session =  sessionmaker(db)
        session = Session()
        fetch = {}


        socialworkers = session.query(socialWorker).filter_by(emailAddress = socialworker_emailaddress).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/telegramid/<socialworker_telegramid>', methods = ['GET'])
def get_socialworkerByTelegramId(socialworker_telegramid):

    # get social worker by telegram id
    try:
        Session =  sessionmaker(db)
        session = Session()

        fetch = {}

        socialworkers = session.query(socialWorker).filter_by(telegramId = socialworker_telegramid).filter_by(isActive = True).filter_by(isDeleted = False).all()
        for socialworker in socialworkers:
            if not socialworker:
                abort(400)
            data = object_as_dict(socialworker)
            # print(data)

            fetch[socialworker.id] = data
            
        resp = Response(json.dumps(fetch) , status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp




@socialworker.route('/socialworker/update/<int:socialworker_id>', methods = ['PATCH'])
def update_socialWorker(socialworker_id):

     # update social worker by id
    try:
        Session =  sessionmaker(db)
        session = Session()

        base_socialworker = session.query(socialWorker).filter_by(id = socialworker_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        if 'ngo_id' in request.form.keys():
            base_socialworker.ngo_id = int(request.form['ngo_id'])
        if 'country_id' in request.form.keys():
            base_socialworker.country_id = int(request.form['country_id'])
        if 'city_id' in request.form.keys():
            base_socialworker.city_id = int(request.form['city_id'])
        if 'type_id' in request.form.keys():
            base_socialworker.type_id = int(request.form['type_id'])
        if 'firstName' in request.form.keys():
            base_socialworker.firstName = request.form['firstName']
        if 'lastName' in request.form.keys():
            base_socialworker.lastName = request.form['lastName']
        if 'userName' in request.form.keys():
            base_socialworker.userName = request.form['userName']
        if 'birthCertificateNumber' in request.form.keys():
            base_socialworker.birthCertificateNumber = request.form['birthCertificateNumber']
        if 'idNumber' in request.form.keys():
            base_socialworker.idNumber = request.form['idNumber']
        if 'idCardUrl' in request.form.keys():
            base_socialworker.idCardUrl = request.form['idCardUrl']
        if 'passportNumber' in request.form.keys():
            base_socialworker.passportNumber = request.form['passportNumber']
        if 'passportUrl' in request.form.keys():
            base_socialworker.passportUrl = request.form['passportUrl']
        if 'gender' in request.form.keys():
            base_socialworker.gender = int(request.form['gender'])
        if 'birthDate' in request.form.keys():
            base_socialworker.birthDate = datetime.datetime.strptime(request.form['birthDate'], '%Y-%m-%d')
        if 'phoneNumber' in request.form.keys():
            base_socialworker.phoneNumber = request.form['phoneNumber']
        if 'emergencyPhoneNumber' in request.form.keys():
            base_socialworker.emergencyPhoneNumber = request.form['emergencyPhoneNumber']
        if 'emailAddress' in request.form.keys():
            base_socialworker.emailAddress = request.form['emailAddress']
        if 'telegramId' in request.form.keys():
            base_socialworker.telegramId = request.form['telegramId']
        if 'postalAddress' in request.form.keys():
            base_socialworker.postalAddress = request.form['postalAddress']
        if 'avatarUrl' in request.form.keys():
            base_socialworker.avatarUrl = request.form['avatarUrl']
        if 'bankAccountNumber' in request.form.keys():
            base_socialworker.bankAccountNumber = request.form['bankAccountNumber']
        if 'bankAccountShebaNumber' in request.form.keys():
            base_socialworker.bankAccountShebaNumber = request.form['bankAccountShebaNumber']
        if 'bankAccountCardNumber' in request.form.keys():
            base_socialworker.bankAccountCardNumber = request.form['bankAccountCardNumber']
        base_socialworker.lastUpdateDate = current_time

        
        res = object_as_dict(base_socialworker)

        resp = Response(json.dumps(res) , status=200)
        session.commit()

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/delete/<int:socialworker_id>', methods = ['PATCH'])
def delete_socialWorker(socialworker_id):

    # delete social worker by id
    try:
        Session =  sessionmaker(db)
        session = Session()

        base_socialworker = session.query(socialWorker).filter_by(id = socialworker_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        base_socialworker.isDeleted = 1

        res = object_as_dict(base_socialworker)

        resp = Response(json.dumps(res) , status=200)
        session.commit()

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp



@socialworker.route('/socialworker/deactive/<int:socialworker_id>', methods = ['PATCH'])
def deactive_socialWorker(socialworker_id):

    # deactive social worker by id
    try:
        Session =  sessionmaker(db)
        session = Session()

        base_socialworker = session.query(socialWorker).filter_by(id = socialworker_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        base_socialworker.isActive = 0

        res = object_as_dict(base_socialworker)

        resp = Response(json.dumps(res) , status=200)
        session.commit()

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp