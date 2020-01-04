import random
from datetime import datetime
from urllib.parse import urljoin

from khayyam import JalaliDate

from . import *
from say.models import session, obj_to_dict
from say.models.child_need_model import ChildNeedModel
from say.models.family_model import FamilyModel
from say.models.need_family_model import NeedFamilyModel
from say.models.need_model import NeedModel
from say.models.payment_model import PaymentModel
from say.models.user_family_model import UserFamilyModel
from say.models.user_model import UserModel
from say.tasks import send_email


def validate_amount(need, amount):
    amount = int(amount)
    need_unpaid = need.cost - need.paid
    if int(amount) > need_unpaid:
        raise ValueError(f"Amount can not be greater that {need_unpaid}")
    if int(amount) < 100:
        raise ValueError("Amount can not be smaller than 100")
    return amount


class GetAllPayment(Resource):
    model = PaymentModel

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @swag_from("./docs/payment/all.yml")
    def get(self):
        args = request.args
        take = args.get('take', 10)
        skip = args.get('skip', 0)
        need_id = args.get('need_id', None)

        try:
            if need_id:
                need_id = int(need_id)
            take = int(take)
            skip = int(skip)
            if take < 1 or skip < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(status=400)

        payments = session.query(self.model) \
            .filter_by(is_verified=True)

        if need_id:
            payments = payments.filter_by(id_need=need_id)

        total_count = payments.count()

        payments = payments \
            .offset(skip) \
            .limit(take)

        result = dict(
            totalCount=total_count,
            payments=[],
        )
        for payment in payments:
            result['payments'].append(obj_to_dict(payment))
        session.close()
        return make_response(
            jsonify(result),
            200,
        )


class GetPayment(Resource):
    model = PaymentModel

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @swag_from("./docs/payment/id.yml")
    def get(self, id):
        payment = session.query(self.model).get(id)
        session.close()
        if payment is None:
            return Response(status=404)

        return make_response(
            jsonify(obj_to_dict(payment)),
            200,
        )


class Payment(Resource):

    @authorize
    @swag_from("./docs/payment/new_payment.yml")
    def post(self):
        user_id = get_user_id()

        resp = make_response({"message": "Something is Wrong!"}, 500)

        if 'needId' not in request.json:
            return make_response(jsonify({"message": "needId is required"}), 500)

        if 'amount' not in request.json:
            return make_response(jsonify({"message": "amount is required"}), 500)

        amount = request.json['amount']
        need_id = request.json['needId']

        try:
            donate = 0
            if 'donate' in request.json:
                donate = int(request.json['donate'])

            if donate < 0:
                resp = make_response(
                    {"message": "Donation Can Not Be Negetive"},
                    500,
                )
                return

            need = session.query(NeedModel).get(need_id)

            if need is None or need.isDeleted:
                resp = make_response({"message": "Need Not Found"}, 500)
                return

            if need.isDone:
                resp = make_response({"message": "Need is already done"}, 500)
                return

            if not need.isConfirmed:
                resp = make_response(
                    jsonify({"message": "error: need is not confirmed yet!"}),
                    500,
                )
                return resp

            user = session.query(UserModel).get(user_id)
            if user is None:
                resp = make_response({"message": "User Not Found"}, 500)
                return

            child_need = (
                session.query(ChildNeedModel)
                .filter_by(id_need=need_id)
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
                .filter_by(id_user=user_id)
                .first()
                is None
            ):
                resp = make_response(jsonify({"message": "payment must be added by the child's family!"}), 500)
                return resp


            try:
                amount = validate_amount(need, amount)
            except ValueError as e:
                resp = make_response(jsonify({"message": str(e)}), 500)
                return

            order_id = str(user.id) \
                + str(need.id) \
                + str(random.randint(100 , 1000))

            total_amount = amount + donate

            api_data = {
                "order_id": order_id,
                "amount": total_amount * 10, # Converting Toman to Rial
                "name": f'{user.firstName} {user.lastName}',
                "phone": user.phoneNumber,
                "mail": user.emailAddress,
                "desc": f'{need.name}-{need.child.generatedCode}-{need.id}',
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
            resp = make_response(str(ex), 500)

        finally:
            session.close()
            return resp


class VerifyPayment(Resource):
    def post(self):
        paymentId = request.form['id']
        orderId = request.form['order_id']

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
        if need.isDone:
            return make_response(dict(message='Need Already Done'), 409)

        amount = pending_payment.amount

        child = child_need.child
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

        need.status = 1
        need.paid += amount
        need.donated += pending_payment.donate

        child.spentCredit += amount

        if need.paid == need._cost:
            need.status = 2
            need.isDone = True
            need.doneAt = datetime.utcnow()

            child.doneNeedCount += 1

            participants = need.get_participants()
            for participate in participants:
                participate.user.doneNeedCount += 1

            need.send_done_email()

        session.commit()

        resp = jsonify(obj_to_dict(pending_payment))

        return make_response(render_template(
            'succesful_payment.html',
            payment=pending_payment,
            user=pending_payment.user,
            need_url=need_url,
        ))


api.add_resource(Payment, "/api/v2/payment")
api.add_resource(GetPayment, "/api/v2/payment/<int:id>")
api.add_resource(GetAllPayment, "/api/v2/payment/all")
api.add_resource(VerifyPayment, "/api/v2/payment/verify")

