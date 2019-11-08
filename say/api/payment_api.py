from urllib.parse import urljoin
import random
from datetime import datetime

from . import *
from say.models.child_need_model import ChildNeedModel
from say.models.family_model import FamilyModel
from say.models.need_family_model import NeedFamilyModel
from say.models.need_model import NeedModel
from say.models.payment_model import PaymentModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel


def validate_amount(need, amount):
    amount = int(amount)
    need_unpaid = need.cost - need.paid
    if int(amount) > need_unpaid:
        raise ValueError(f"Amount can not be greater that {need_unpaid}")
    if int(amount) < 100:
        raise ValueError("Amount can not be smaller than 100")
    return amount


class Payment(Resource):

    @swag_from("./docs/payment/new_payment.yml")
    def post(self):
        resp = {"message": "Something is Wrong!"}
        if 'needId' not in request.json:
            return jsonify({"message": "needId is required"})

        if 'userId' not in request.json:
            return jsonify({"message": "userId is required"})

        if 'amount' not in request.json:
            return jsonify({"message": "amount is required"})

        amount = request.json['amount']
        userId = request.json['userId']
        needId = request.json['needId']

        session_maker = sessionmaker(db)
        session = session_maker()

        try:
            donate = 0
            if 'donate' in request.json:
                donate = int(request.json['donate'])

            if donate < 0:
                resp = {"message": "Donation Can Not Be Negetive"}
                return

            need = session.query(NeedModel).get(needId)
            if need is None:
                resp = {"message": "Need Not Found"}
                return

            if not need.isConfirmed:
                resp = make_response(
                    jsonify({"message": "error: need is not confirmed yet!"}),
                    422,
                )
                return resp

            user = session.query(UserModel).get(userId)
            if user is None:
                resp = {"message": "User Not Found"}
                return

            child_need = (
                session.query(ChildNeedModel)
                .filter_by(id_need=needId)
                .first()
            )

            family = (
                session.query(FamilyModel)
                .filter_by(id_child=child_need.id_child)
                .filter_by(isDeleted=False)
                .first()
            )

            if (
                session.query(UserFamilyModel)
                .filter_by(isDeleted=False)
                .filter_by(id_family=family.id)
                .filter_by(id_user=userId)
                .first()
                is None
            ):
                resp = make_response(jsonify({"message": "payment must be added by the child's family!"}), 422)
                return resp


            try:
                amount = validate_amount(need, amount)
            except ValueError as e:
                resp = make_response(jsonify({"message": str(e)}), 422)
                return

            order_id = str(user.id) \
                + str(need.id) \
                + str(random.randint(100 , 1000))

            total_amount = amount + donate

            api_data = {
                "order_id": order_id,
                "amount": total_amount * 10, # Converting Toman to Rial
                "name": user.lastName,
                "phone": user.phoneNumber,
                "mail": 'info@say.company',
                "desc": need.name,
                "callback": urljoin(app.config['BASE_URL'], 'api/v2/payment/verify'),
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
                donate=donate,
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
            resp = make_response(str(ex), 422)

        finally:
            session.close()
            return resp


class VerifyPayment(Resource):
    def post(self):
        paymentId = request.form['id']
        orderId = request.form['order_id']

        session_maker = sessionmaker(db)
        session = session_maker()

        pending_payment = session.query(PaymentModel) \
            .filter_by(paymentId = paymentId) \
            .first()

        if pending_payment is None:
            resp = dict(message='Invalid Payment ID')
            return make_response(resp, 422)


        child_need = session.query(ChildNeedModel) \
            .filter_by(id_need = pending_payment.need.id) \
            .first()

        need = pending_payment.need
        amount = pending_payment.amount

        child = child_need.child_relation
        need_url = f"/needPage/{need.id}/{child.id}/{pending_payment.id_user}"
        response = idpay.verify(paymentId, orderId)
        if 'error_code' in response or response['status'] != 100:
            #  TODO: what happens after unsusscesful payment
            return redirect(need_url, 302)

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

        family = (
            session.query(FamilyModel)
            .filter_by(id_child=child.id)
            .filter_by(isDeleted=False)
            .first()
        )

        participant = (
            session.query(NeedFamilyModel)
            .filter_by(id_need=pending_payment.id_need)
            .filter_by(id_user=pending_payment.id_user)
            .filter_by(isDeleted=False)
            .first()
        )
        if participant is None:
            new_participant = NeedFamilyModel(
                id_family=family.id,
                id_user=pending_payment.id_user,
                id_need=pending_payment.id_need,
            )
            session.add(new_participant)

        need.paid += amount
        child.spentCredit += amount
        need.progress = need.paid / need.cost * 100

        if need.paid == need.cost:
            need.isDone = True
            # user.doneNeedCount += 1  # TODO: which one is correct?

            participants = (
                session.query(NeedFamilyModel)
                .filter_by(id_need=need.id)
                .filter_by(isDeleted=False)
                .all()
            )

            for participate in participants:
                participate.user_relation.doneNeedCount += 1

        session.commit()

        resp = jsonify(obj_to_dict(pending_payment))

        return make_response(render_template(
            'succesful_payment.html',
            payment=pending_payment,
            user=pending_payment.user,
            need_url=need_url,
        ))

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

