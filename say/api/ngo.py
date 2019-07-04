import os
from say.models import NGO
from say.config import db
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from flask import Flask, Blueprint, json, Response, request, abort
import requests
import datetime

current_time = datetime.datetime.now()


ngo = Blueprint('ngo', __name__)

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}

@ngo.route('/ngo', methods = ['GET', 'POST'])
def api_ngo():

    if request.method == 'GET':
        # get all ngo

        Session =  sessionmaker(db)
        session = Session()

        try:
           
            base_ngos = session.query(NGO).filter_by(isActive = True).filter_by(isDeleted = False).all()

            fetch = {}
            
            for n in base_ngos:

                data = object_as_dict(n)
                fetch[n.id] = data
            print(fetch)
            resp = Response(json.dumps(fetch), status=200)
        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}))
        finally:
            session.close()
            return resp



    elif request.method == 'POST':
        # insert ngo

        Session =  sessionmaker(db)
        session = Session()
        
        try:
            name = request.form['name']
            country_id = int(request.form['country_id'])
            city_id = int(request.form['city_id'])
            coordinator_id = int(request.form['coordinator_id'])
            postalAddress = request.form['postalAddress']
            emailAddress = request.form['emailAddress']
            phoneNumber = request.form['phoneNumber']
            logoUrl = request.form['logoUrl']
            balance = int(request.form['balance'])
            socialWorkerCount = '0'
            childrenCount = '0'
            registerDate = current_time
            lastUpdateDate = current_time
            isActive = int(request.form['isActive'])
            isDeleted = 0


            new_ngo = NGO(
                name = name,
                country_id = country_id,
                city_id = city_id,
                coordinator_id = coordinator_id,
                postalAddress = postalAddress,
                emailAddress = emailAddress,
                phoneNumber = phoneNumber,
                logoUrl = logoUrl,
                balance = balance,
                socialWorkerCount = socialWorkerCount,
                childrenCount = childrenCount,
                registerDate = registerDate,
                lastUpdateDate = lastUpdateDate,
                isActive = isActive,
                isDeleted = isDeleted
            )

            session.add(new_ngo)
            session.commit() 

            res = {'msg' : 'ngo is created'}
            resp = Response(json.dumps(res) , status=200, headers={'Access-Control-Allow-Origin': '*'})    

        except Exception as e:
            print(e)
            resp = Response(json.dumps({'msg': 'sth is wrong!'}))

        finally:
            session.close()
            return resp



@ngo.route('/ngo/id/<int:ngo_id>', methods = ['GET'])
def get_ngoById(ngo_id):

    # get ngo by id

    Session =  sessionmaker(db)
    session = Session()

    try:
        base_ngo = session.query(NGO).filter_by(id = ngo_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        if not base_ngo:
            abort(400)
        resp = Response(json.dumps(object_as_dict(base_ngo)), status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'msg': 'sth is wrong!'}))

    finally:
        session.close()
        return resp



@ngo.route('/ngo/coordinator/<int:ngo_coordinatorid>', methods = ['GET'])
def get_ngoByCoordinatorId(ngo_coordinatorid):

    # get ngo by coordinator_id

    Session =  sessionmaker(db)
    session = Session()


    try:
        fetch = {}
        
        base_ngos = session.query(NGO).filter_by(coordinator_id = ngo_coordinatorid).filter_by(isActive = True).filter_by(isDeleted = False).all()

        for n in base_ngos:
            if not n:
                abort(400)
            data = object_as_dict(n)

            fetch[n.id] = data

        resp = Response(json.dumps(fetch), status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)

    finally:
        session.close()
        return resp



@ngo.route('/ngo/name/<ngo_name>', methods = ['GET'])
def get_ngoByName(ngo_name):

    # get ngo by name

    Session =  sessionmaker(db)
    session = Session()


    try:
        fetch = {}
        
        base_ngos = session.query(NGO).filter_by(name = ngo_name).filter_by(isActive = True).filter_by(isDeleted = False).all()

        for n in base_ngos:
            if not n:
                abort(400)
            data = object_as_dict(n)

            fetch[n.id] = data

        resp = Response(json.dumps(fetch), status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)

    finally:
        session.close()
        return resp




@ngo.route('/ngo/phonenumber/<ngo_phonenumber>', methods = ['GET'])
def get_ngoByPhoneNumber(ngo_phonenumber):

    # get ngo by Phone Number

    Session =  sessionmaker(db)
    session = Session()


    try:
        fetch = {}
        
        base_ngos = session.query(NGO).filter_by(phoneNumber = ngo_phonenumber).filter_by(isActive = True).filter_by(isDeleted = False).all()

        for n in base_ngos:
            if not n:
                abort(400)
            data = object_as_dict(n)

            fetch[n.id] = data

        resp = Response(json.dumps(fetch), status=200)

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'msg': 'sth is wrong!'}), status=500)

    finally:
        session.close()
        return resp







@ngo.route('/ngo/update/<int:ngo_id>', methods = ['PATCH'])
def update_NGO(ngo_id):

     # update ngo by id
    
    Session =  sessionmaker(db)
    session = Session()

    
    try:
        base_ngo = session.query(NGO).filter_by(id = ngo_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        if 'country_id' in request.form.keys():
            base_ngo.country_id = int(request.form['country_id'])
        if 'city_id' in request.form.keys():
            base_ngo.city_id = int(request.form['city_id'])
        if 'coordinator_id' in request.form.keys():
            base_ngo.coordinator_id = int(request.form['coordinator_id'])
        if 'name' in request.form.keys():
            base_ngo.name = request.form['name']
        if 'postalAddress' in request.form.keys():
            base_ngo.postalAddress = request.form['postalAddress']
        if 'emailAddress' in request.form.keys():
            base_ngo.emailAddress = request.form['emailAddress']
        if 'phoneNumber' in request.form.keys():
            base_ngo.phoneNumber = request.form['phoneNumber']
        if 'logoUrl' in request.form.keys():
            base_ngo.logoUrl = request.form['logoUrl']
        if 'balance' in request.form.keys():
            base_ngo.balance = request.form['balance']
        base_ngo.lastUpdateDate = current_time
        

        
        res = object_as_dict(base_ngo)

        resp = Response(json.dumps(res) , status=200)
        session.commit()

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp






@ngo.route('/ngo/delete/<int:ngo_id>', methods = ['PATCH'])
def delete_NGO(ngo_id):

    # delete NGO by id
    Session =  sessionmaker(db)
    session = Session()

    try:

        base_ngo = session.query(NGO).filter_by(id = ngo_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        base_ngo.isDeleted = 1

        res = object_as_dict(base_ngo)

        resp = Response(json.dumps(res) , status=200)
        session.commit()

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp





@ngo.route('/ngo/deactive/<int:ngo_id>', methods = ['PATCH'])
def deactive_NGO(ngo_id):

    # deactivate NGO by id
    Session =  sessionmaker(db)
    session = Session()

    try:

        base_ngo = session.query(NGO).filter_by(id = ngo_id).filter_by(isActive = True).filter_by(isDeleted = False).first()

        base_ngo.isActive = 0

        res = object_as_dict(base_ngo)

        resp = Response(json.dumps(res) , status=200)
        session.commit()

    except Exception as e:
        print(e)
        resp = Response(json.dumps({'message' : 'error'}) , status= 500)
    finally:
        session.close()
        return resp