from datetime import datetime
import random

from wtforms import Form, IntegerField, StringField, DecimalField, validators
from say.models.need_model import NeedModel
from say.models.user_model import UserModel
from say.models.child_need_model import ChildNeedModel
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
                "callback": f"{app.config['BASE_URL']}/api/v2/payment/verify"
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
            resp = jsonify(obj_to_dict(new_payment))
            resp.headers.add("Access-Control-Allow-Origin", "*")
            resp.headers.add(
                "Access-Control-Allow-Headers",
                "Origin, X-Requested-With, Content-Type, Accept",
            )

        except Exception as ex:
            resp = str(ex)

        finally:
            session.close()
            return resp


class VerifyPayment(Resource):
    def post(self):
        paymentId = request.form['id']
        orderId = request.form['order_id']

        response = idpay.verify(paymentId, orderId)
        if response['status'] != 100:
            resp = make_response(
                jsonify(dict(message=idpay.RESPONSES[response['status']]))
            )
            return resp

        session_maker = sessionmaker(db)
        session = session_maker()

        pending_payment = session.query(PaymentModel) \
            .filter_by(paymentId = paymentId) \
            .first()

        if pending_payment is None:
            resp = dict(message='Invalid orderId')
            return resp

        pending_payment.is_verified = True
        pending_payment.date = datetime.fromtimestamp(int(
            response['date']
        ))
        pending_payment.track_id = response['track_id']
        pending_payment.verified_date = datetime.fromtimestamp(int(
            response['verify']['date']
        ))
        pending_payment.card_no = response['payment']['card_no']
        pending_payment.hashed_card_no = response['payment']['hashed_card_no']
        session.commit()

        child_id = session.query(ChildNeedModel) \
            .filter_by(id_need = pending_payment.need.id) \
            .first() \
            .id_child
        resp = jsonify(obj_to_dict(pending_payment))
        return make_response(render_template(
            'succesful_payment.html',
            payment=pending_payment,
        ))
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
api.add_resource(VerifyPayment, "/api/v2/payment/verify")

