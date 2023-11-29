import random
import string
from datetime import datetime
from urllib.parse import urljoin

import requests
from flasgger import swag_from
from flask import make_response
from flask import request
from flask_restful import Resource

from say.locale import DEFAULT_LOCALE
from say.models import commit
from say.models import obj_to_dict
from say.models.family_model import Family
from say.models.need_model import Need
from say.models.payment_model import Payment
from say.models.user_family_model import UserFamily
from say.models.user_model import User
from say.render_template_i18n import render_template_i18n
from say.schema.payment import NewPaymentSchema

from ..authorization import authorize
from ..authorization import get_user_id
from ..config import configs
from ..decorators import json
from ..decorators import validate
from ..exceptions import HTTP_NOT_FOUND
from ..exceptions import AmountTooHigh
from ..exceptions import AmountTooLow
from ..exceptions import HTTPException
from ..orm import session
from ..roles import ADMIN
from ..roles import SAY_SUPERVISOR
from ..roles import SUPER_ADMIN
from .ext import api
from .ext import idpay
from .ext import zibal


def validate_amount(need, amount):
    amount = int(amount)
    need_unpaid = need.cost - need.paid
    if int(amount) > need_unpaid:
        raise AmountTooHigh(f"Amount can not be greater that {need_unpaid}")
    if int(amount) < configs.MIN_BANK_AMOUNT:
        raise AmountTooLow(f"Amount can not be smaller than {configs.MIN_BANK_AMOUNT}")
    return amount


def generate_order_id(N=configs.PAYMENT_ORDER_ID_LENGTH):
    """
    Generate a random string containing lowercase, uppercase and digits
    """

    while True:
        order_id = "".join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits
            )
            for _ in range(N)
        )

        if not check_order_id_exist(order_id):
            return order_id


def check_order_id_exist(order_id):
    return session.query(Payment).filter(Payment.order_id == order_id).one_or_none()


class GetAllPayment(Resource):
    model = Payment

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from("./docs/payment/all.yml")
    def get(self):
        args = request.args
        take = args.get("take", 10)
        skip = args.get("skip", 0)
        need_id = args.get("need_id", None)

        try:
            if need_id:
                need_id = int(need_id)
            take = int(take)
            skip = int(skip)
            if take < 1 or skip < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return {"message": "Invalid skip or take"}, 400

        payments = session.query(Payment).filter(Payment.verified.isnot(None))

        if need_id:
            payments = payments.filter_by(id_need=need_id)

        total_count = payments.count()

        payments = payments.offset(skip).limit(take)

        result = dict(
            totalCount=total_count,
            payments=list(),
        )
        for payment in payments:
            result["payments"].append(obj_to_dict(payment))
        session.close()
        return result


class GetPayment(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)
    @json
    @swag_from("./docs/payment/id.yml")
    def get(self, id):
        payment = session.query(Payment).get(id)
        session.close()
        if payment is None:
            raise HTTP_NOT_FOUND()

        return payment


class AddPayment(Resource):
    @authorize
    @validate(NewPaymentSchema)
    @json
    @commit
    @swag_from("./docs/payment/new_payment.yml")
    def post(self, data: NewPaymentSchema):
        user_id = get_user_id()

        need_amount = data.amount
        need_id = data.need_id
        donation = data.donate
        use_credit = data.use_credit
        gateWay = data.gateWay  # added for second payment gateway

        need = session.query(Need).get(need_id)
        if need is None or need.isDeleted:
            return {"message": "Need Not Found"}, 400

        if need.isDone:
            return {"message": "Need is already done"}, 422

        if not need.isConfirmed:
            return {"message": "error: need is not confirmed yet!"}, 422

        user = session.query(User).get(user_id)
        if user is None:
            return {"message": "User Not Found"}

        family = (
            session.query(Family)
            .filter_by(id_child=need.child_id)
            .filter_by(isDeleted=False)
            .one()
        )

        if (
            session.query(UserFamily)
            .filter_by(isDeleted=False)
            .filter_by(id_family=family.id)
            .filter_by(id_user=user_id)
            .first()
            is None
        ):
            return {"message": "payment must be added by the child's family!"}, 422

        try:
            need_amount = validate_amount(need, need_amount)
        except ValueError as e:
            return {"message": str(e)}, 422

        desc = f"{need.name}-{need.child.sayName}"
        name = f"{user.firstName} {user.lastName}"
        callback = urljoin(configs.API_URL, "api/v2/payment/verify")

        credit = 0
        if use_credit:
            credit = min(user.credit, need_amount + donation)

        payment = Payment(
            user=user,
            need=need,
            need_amount=need_amount,
            donation_amount=donation,
            credit_amount=credit,
            desc=desc,
            order_id=generate_order_id(),
        )
        session.add(payment)
        session.flush()

        if payment.bank_amount == 0:
            payment.verify()

            success_payment = render_template_i18n(
                "successful_payment.html",
                payment=payment,
                user=user,
                locale=user.locale,
            )
            return {"response": success_payment}, 299

        # Save some credit for the user
        if payment.bank_amount < configs.MIN_BANK_AMOUNT:
            payment.credit_amount -= configs.MIN_BANK_AMOUNT - payment.bank_amount

        # idpay gateway
        if gateWay == 1:
            api_data = {
                "order_id": payment.order_id,
                "amount": payment.bank_amount,
                "name": name,
                "desc": desc,
                "callback": callback,
            }

            transaction = idpay.new_transaction(**api_data)
            if "error_code" in transaction:
                raise HTTPException(
                    status_code=422,
                    message=idpay.ERRORS[transaction["error_code"]],
                )

            payment.gateway_payment_id = transaction["id"]
            payment.link = transaction["link"]

        # zibal gateway
        if gateWay == 2:
            zibal_request = zibal.request(payment.bank_amount, payment.order_id, desc)
            if int(zibal_request["result"]) != 100:
                raise HTTPException(
                    status_code=422,
                    message=zibal.ERRORS[zibal_request["result"]],
                )
            if int(zibal_request["result"]) == 100:
                trackId = zibal_request["trackId"]
                link = urljoin("https://gateway.zibal.ir/start/", str(trackId))
                payment.gateway_payment_id = trackId
                payment.link = link

        return payment


class VerifyPayment(Resource):
    @staticmethod
    def _verify_payment(payment_id, order_id, gateway):
        unsuccessful_response = render_template_i18n(
            "unsuccessful_payment.html",
            locale=DEFAULT_LOCALE,
        )

        if not payment_id or not order_id:
            return make_response(unsuccessful_response)

        pending_payment = (
            session.query(Payment)
            .filter(
                Payment.gateway_payment_id == payment_id,
                Payment.order_id == order_id,
                Payment.cart_payment_id.is_(None),
                Payment.verified.is_(None),
            )
            .with_for_update()
            .one_or_none()
        )

        if pending_payment is None:
            return make_response(unsuccessful_response)

        user = session.query(User).with_for_update().get(pending_payment.id_user)
        need = session.query(Need).with_for_update().get(pending_payment.id_need)

        if need.isDone:
            return make_response(unsuccessful_response)
        if gateway == 1:
            try:
                response = idpay.verify(
                    pending_payment.gateway_payment_id,
                    pending_payment.order_id,
                )
            except requests.exceptions.RequestException:
                return make_response(unsuccessful_response)

            if (
                not response
                or "error_code" in response
                or response["status"]
                not in (
                    100,
                    101,
                    200,
                )
            ):
                return make_response(unsuccessful_response)

            transaction_date = datetime.fromtimestamp(int(response["date"]))
            gateway_track_id = response["track_id"]
            verified = datetime.fromtimestamp(int(response["verify"]["date"]))
            card_no = response["payment"]["card_no"]
            hashed_card_no = response["payment"]["hashed_card_no"]

        if gateway == 2:
            try:
                response = zibal.verify(
                    pending_payment.gateway_payment_id,
                )
            except requests.exceptions.RequestException:
                return make_response(unsuccessful_response)

            if response["message"] != "success":
                return make_response(unsuccessful_response)

            transaction_date = response["paidAt"]
            gateway_track_id = request.args.get("trackId")
            verified = response["paidAt"]
            card_no = response["cardNumber"]
            hashed_card_no = response["cardNumber"]

        pending_payment.verify(
            transaction_date,
            gateway_track_id,
            verified,
            card_no,
            hashed_card_no,
        )

        need.payments.append(pending_payment)
        return make_response(
            render_template_i18n(
                "successful_payment.html",
                payment=pending_payment,
                user=user,
                locale=user.locale,
            )
        )

    @json
    @commit
    def post(self):
        gate_one_payment_id = request.form.get("id")
        gate_one_order_id = request.form.get("order_id")
        gate_two_payment_id = request.args.get("trackId")
        gate_two_order_id = request.args.get("orderId")
        if gate_one_payment_id:
            return self._verify_payment(gate_one_payment_id, gate_one_order_id, 1)
        if gate_two_payment_id:
            return self._verify_payment(gate_two_payment_id, gate_two_order_id, 2)

    @json
    @commit
    def get(self):
        gate_one_payment_id = request.form.get("id")
        gate_one_order_id = request.form.get("order_id")
        gate_two_payment_id = request.args.get("trackId")
        gate_two_order_id = request.args.get("orderId")
        if gate_two_payment_id is None:
            return self._verify_payment(gate_one_payment_id, gate_one_order_id, 1)
        if gate_two_payment_id:
            return self._verify_payment(gate_two_payment_id, gate_two_order_id, 2)


api.add_resource(AddPayment, "/api/v2/payment")
api.add_resource(GetPayment, "/api/v2/payment/<int:id>")
api.add_resource(GetAllPayment, "/api/v2/payment/all")
api.add_resource(VerifyPayment, "/api/v2/payment/verify")
