from datetime import datetime
import random

from wtforms import Form, IntegerField, StringField, DecimalField, validators
from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from say.models.payment_model import PaymentModel
from . import *


#    needId = IntegerField('needId', [
#        validators.DataRequired()
#    ])
#    userId = IntegerField('userId', [
#        validators.DataRequired(message=('userId الزامیست!'))
#    ])
#    amount = DecimalField('amount', [
#        validators.DataRequired(message=('amount الزامیست!'))
#    ])
#
#    def validate_needId(self, needId):
#        from pudb import set_trace; set_trace()
#        session_maker = sessionmaker(db)
#        session = session_maker()
#        need = session.query(NeedModel).get(needId)
#        session.close()
#        if need is None:
#            raise ValueError("Need Not Found")
#
#    def validate_userId(self, userId):
#        session_maker = sessionmaker(db)
#        session = session_maker()
#        user = session.query(UserModel).get(userId)
#        session.close()
#        if user is None:
#            raise ValueError("User Not Found")
#
def validate_amount(need, amount):
    amount = int(amount)
    need_unpaid = need.cost - need.paid
    if int(amount) > need_unpaid:
        raise ValueError(f"Amount can not be greater that {need_unpaid}")
    if int(amount) < 1000:
        raise ValueError("Amount can not be smaller than 1000")
    return amount


class Payment(Resource):

    @swag_from("./docs/payment/new_payment.yml")
    def post(self):
        resp = {"message": "Something is Wrong!"}
        if 'needId' not in request.form:
            return jsonify({"message": "needId الزامیست!"})

        if 'userId' not in request.form:
            return jsonify({"message": "userId الزامیست!"})

        if 'amount' not in request.form:
            return jsonify({"message": "amount الزامیست!"})

        amount = request.form['amount']
        userId = request.form['userId']
        needId = request.form['needId']

        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            need = session.query(NeedModel).get(needId)
            if need is None:
                resp = {"message": "Need Not Found"}
                return

            user = session.query(UserModel).get(userId)
            if user is None:
                resp = {"message": "User Not Found"}
                return

            try:
                amount = validate_amount(need, amount)
            except ValueError as e:
                resp = {"message": str(e)}
                return


            order_id = str(user.id) \
                + str(need.id) \
                + str(random.randint(1 , 1000))

            api_data = {
                "order_id": order_id,
                "amount": amount,
                "name": user.lastName,
                "phone": user.phoneNumber,
                "mail": 'info@say.company',
                "desc": need.name,
                "callback": "http://sayapp.company/payment/callback"
            }

            new_transaction = idpay.new_transaction(**api_data)

            new_payment = PaymentModel(
                createdAt=datetime.utcnow(),
                paymentId=new_transaction['id'],
                id_user=user.id,
                id_need=need.id,
                orderId=order_id,
                link=new_transaction['link'],
                amount=amount,
                desc=api_data['desc'],
            )
            session.add(new_payment)
            session.commit()
            resp = redirect(new_payment.link, code=302)

        except Exception as ex:
            resp = str(ex)

        finally:
            session.close()
            return resp

#
#@app.route('/verify' , methods = ['POST'])
#def verify():
#    id = request.form['id']
#    orderId = request.form['orderId']
#
#    api_url = 'https://api.idpay.ir/v1.1/payment/verify'
#    api_headers = { 'Content-Type': 'application/json' , 'X-API-KEY':'c999970e-64d2-477b-8852-447594fb730b', 'X-SANDBOX': '1'}
#    api_data = {'id' : id , 'order_id' : orderId}
#
#    api_respond = requests.post(api_url , headers = api_headers , json= api_data)
#    api_respond = api_respond.json()
#
#    resp = Response(json.dumps(api_respond), status=200, mimetype='application/json')
#
#    print(api_respond)
#
#    Session = sessionmaker(db)
#    session = Session()
#
#    base.metadata.create_all(db)
#
#    pending_payment = session.query(PaymentDB).filter_by(orderId = orderId).first()
#    pending_payment.is_verified = True
#    pending_payment.data = api_respond['date']
#    pending_payment.track_id = api_respond['track_id']
#    pending_payment.verified_date = api_respond['verify']['date']
#    pending_payment.card_no = api_respond['payment']['card_no']
#    pending_payment.hashed_card_no = api_respond['payment']['hashed_card_no']
#    session.commit()
#    session.close()
#
#
#    return resp
#
#
#@app.route('/payment/user/<int:user_id>' , methods =  ['GET'])
#def getPaymentByUserId(user_id):
#    try :
#        Session = sessionmaker(db)
#        session = Session()
#
#        base.metadata.create_all(db)
#
#        user_payment_data = session.query(paymentDB).filter_By(userId = user_id).all()
#        user_payment_data = object_as_dict(user_payment_data)
#
#        resp = Response(json.dumps(user_payment_data) , status= 200 , mimetype='application/json')
#
#    except Exception as e :
#        print(e)
#        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status= 500)
#
#    finally :
#        return resp
#
#
#@app.route('/payment/need/<int:need_id>' , methods =  ['GET'])
#def getPaymentByNeedId(need_id):
#    try :
#        Session = sessionmaker(db)
#        session = Session()
#
#        base.metadata.create_all(db)
#
#        need_payment_data = session.query(paymentDB).filter_By(needId = need_id).all()
#        need_payment_data = object_as_dict(user_payment_data)
#
#        resp = Response(json.dumps(need_payment_data) , status= 200 , mimetype='application/json')
#
#    except Exception as e :
#        print(e)
#        resp = Response(json.dumps({'message' : 'something is wrong !!!'}) , status= 500)
#
#    finally :
#        return resp
#


api.add_resource(Payment, "/api/v2/payment")
