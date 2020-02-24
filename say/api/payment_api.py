from datetime import datetime
from urllib.parse import urljoin

from werkzeug.exceptions import abort

from . import *
from say.models import session, obj_to_dict, commit
from say.models.child_need_model import ChildNeed
from say.models.family_model import Family
from say.models.need_model import Need
from say.models.payment_model import Payment
from say.models.user_family_model import UserFamily
from say.models.user_model import User
from say.render_template_i18n import render_template_i18n


def validate_amount(need, amount):
    amount = int(amount)
    need_unpaid = need.cost - need.paid
    if int(amount) > need_unpaid:
        raise ValueError(f"Amount can not be greater that {need_unpaid}")
    if int(amount) < idpay.MIN_AMOUNT:
        raise ValueError("Amount can not be smaller than 100")
    return amount


class GetAllPayment(Resource):
    model = Payment

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
            .filter_by(verified.isnot(None))

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
    model = Payment

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


class AddPayment(Resource):

    @authorize
    @commit
    @swag_from("./docs/payment/new_payment.yml")
    def post(self):
        user_id = get_user_id()

        resp = {"message": "Something is Wrong!"}

        if 'needId' not in request.json:
            return jsonify({"message": "needId is required"})

        if 'amount' not in request.json:
            return jsonify({"message": "amount is required"})

        need_amount = request.json['amount']
        need_id = request.json['needId']

        use_credit = bool(request.json.get('useCredit', True))

        donation = 0
        if 'donate' in request.json:
            donation = int(request.json['donate'])

        if donation < 0:
            return {"message": "Donation Can Not Be Negetive"}

        need = session.query(Need) \
            .with_for_update() \
            .get(need_id)

        if need is None or need.isDeleted:
            return {"message": "Need Not Found"}

        if need.isDone:
            return {"message": "Need is already done"}

        if not need.isConfirmed:
            return make_response(
                jsonify({"message": "error: need is not confirmed yet!"}),
                422,
            )
            return resp

        user = session.query(User).get(user_id)
        if user is None:
            return {"message": "User Not Found"}

        child_need = (
            session.query(ChildNeed)
            .filter_by(id_need=need_id)
            .first()
        )

        family = (
            session.query(Family)
            .filter_by(id_child=child_need.id_child)
            .filter_by(isDeleted=False)
            .first()
        )

        if (
            session.query(UserFamily)
            .filter_by(isDeleted=False)
            .filter_by(id_family=family.id)
            .filter_by(id_user=user_id)
            .first()
            is None
        ):
            return make_response(jsonify({"message": "payment must be added by the child's family!"}), 422)

        try:
            need_amount = validate_amount(need, need_amount)
        except ValueError as e:
            return make_response(jsonify({"message": str(e)}), 422)

        desc = f'{need.name}-{need.child.sayName}'
        name = f'{user.firstName} {user.lastName}'
        callback = urljoin(app.config['BASE_URL'], 'api/v2/payment/verify')

        credit = 0
        if use_credit:
            credit = min(user.credit, need_amount +  donation)

        payment = Payment(
            user=user,
            need=need,
            need_amount=need_amount,
            donation_amount=donation,
            credit_amount=credit,
            desc=desc,
            use_credit=use_credit,
        )
        session.add(payment)
        session.flush()

        if payment.bank_amount == 0:
            payment.verify()

            success_payment = render_template_i18n(
                'successful_payment.html',
                payment=payment,
                user=user,
                locale=user.locale,
            )
            return make_response({'response': success_payment}, 299)

        # Save some credit for the user
        if payment.bank_amount < idpay.MIN_AMOUNT:
            payment.credit_amount -= idpay.MIN_AMOUNT - payment.bank_amount

        api_data = {
            "order_id": payment.order_id,
            "amount": payment.bank_amount,
            "name": name,
            "desc": desc,
            "callback": callback,
        }

        transaction = idpay.new_transaction(**api_data)
        if 'error_code' in transaction:
            raise Exception(idpay.ERRORS[transaction['error_code']])

        payment.gateway_payment_id=transaction['id']
        payment.link=transaction['link']

        resp = jsonify(obj_to_dict(payment))

        resp.headers.add("Access-Control-Allow-Origin", "*")
        resp.headers.add(
            "Access-Control-Allow-Headers",
            "Origin, X-Requested-With, Content-Type, Accept",
        )

        return resp

class VerifyPayment(Resource):
    @commit
    def post(self):
        paymentId = request.form['id']
        order_id = request.form['order_id']

        pending_payment = session.query(Payment) \
            .filter_by(gateway_payment_id=paymentId) \
            .with_for_update() \
            .first()

        if pending_payment is None:
            abort(404)

        user = session.query(User) \
            .with_for_update() \
            .get(pending_payment.id_user)

        need = session.query(Need) \
            .with_for_update() \
            .get(pending_payment.id_need)

        unsuccessful_response = render_template_i18n(
            'unsuccessful_payment.html',
            payment=pending_payment,
            user=user,
            locale=user.locale,
        )

        if need.isDone:
            return make_response(unsuccessful_response)

        try:
            response = idpay.verify(
                pending_payment.gateway_payment_id,
                pending_payment.order_id,
            )
        except:
            return make_response(unsuccessful_response)

        if not response or 'error_code' in response or response['status'] != 100:
            return make_response(unsuccessful_response)

        transaction_date = datetime.fromtimestamp(
            int(response['date']),
        )
        gateway_track_id = response['track_id']
        verified = datetime.fromtimestamp(
            int(response['verify']['date']),
        )
        card_no = response['payment']['card_no']
        hashed_card_no = response['payment']['hashed_card_no']

        pending_payment.verify(
            transaction_date,
            gateway_track_id,
            verified,
            card_no,
            hashed_card_no,
        )

        need.payments.append(pending_payment)

        return make_response(render_template_i18n(
            'successful_payment.html',
            payment=pending_payment,
            user=user,
            locale=user.locale,
        ))


api.add_resource(AddPayment, "/api/v2/payment")
api.add_resource(GetPayment, "/api/v2/payment/<int:id>")
api.add_resource(GetAllPayment, "/api/v2/payment/all")
api.add_resource(VerifyPayment, "/api/v2/payment/verify")

