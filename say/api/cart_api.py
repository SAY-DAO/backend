from datetime import datetime
from urllib.parse import urljoin

import requests
from flasgger import swag_from
from flask import make_response
from flask import request
from flask_restful import Resource

from say.api.ext import api
from say.api.ext import limiter
from say.api.payment_api import generate_order_id
from say.authorization import authorize
from say.authorization import get_user_id
from say.config import configs
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.exceptions import HTTPException
from say.locale import DEFAULT_LOCALE
from say.models import Cart
from say.models import CartNeed
from say.models import Child
from say.models import Family
from say.models import Need
from say.models import Payment
from say.models import UserFamily
from say.models import commit
from say.models.cart import CartPayment
from say.orm import session
from say.render_template_i18n import render_template_i18n
from say.roles import USER
from say.schema.cart import CartNeedInputSchema
from say.schema.cart import CartPaymentInSchema
from say.schema.cart import CartPaymentSchema
from say.schema.cart import CartPutSchema
from say.schema.cart import CartSchema

from .ext import idpay


def payable_needs(session, user_id, need_ids):
    needs = (
        session.query(Need)
        .join(Child)
        .join(Family)
        .join(UserFamily)
        .filter(
            Need.id.in_(need_ids),
            Need.isDeleted.is_(False),
            Need.isConfirmed.is_(True),
            Need.unpayable.is_(False),
            Need.isDone.is_(False),
            UserFamily.id_user == user_id,
            UserFamily.isDeleted.is_(False),
        )
        .all()
    )

    return needs


class CartAPI(Resource):
    decorators = [limiter.limit('15/minute')]

    @authorize(USER)
    @json
    @swag_from('./docs/cart/get.yml')
    def get(self):
        user_id = get_user_id()
        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
        return CartSchema.from_orm(cart)

    @authorize(USER)
    @json
    @swag_from('./docs/cart/put.yml')
    def put(self):
        try:
            data = CartPutSchema(**request.json)
        except ValueError as e:
            return e.json(), 400
        except TypeError:
            return 'No Data in Body', 400

        user_id = get_user_id()
        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
        needs = payable_needs(session, user_id, data.need_ids)
        if len(needs) != len(data.need_ids):
            return {
                'invalidNeedIds': list(set(data.need_ids) - set([n.id for n in needs]))
            }, 600

        cart_needs = (
            session.query(CartNeed)
            .filter(
                CartNeed.cart_id == cart.id,
                CartNeed.deleted.is_(None),
            )
            .all()
        )

        for cart_need in cart_needs:
            cart_need.deleted = datetime.utcnow()

        for need in needs:
            cart_need = CartNeed(need=need, cart=cart)
            session.add(cart_need)

        session.flush()
        session.expire(cart)
        return CartSchema.from_orm(cart)


class CartNeedsAPI(Resource):
    @authorize(USER)
    @json
    @commit
    @swag_from('./docs/cart/add.yml')
    def post(self):
        try:
            data = CartNeedInputSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        user_id = get_user_id()
        needs = payable_needs(session, user_id, [data.need_id])

        if len(needs) != 1:
            raise HTTPException(400, f'Can not add need {data.need_id} to cart')

        need = needs[0]
        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
        cart_need = (
            session.query(CartNeed)
            .filter(
                CartNeed.cart_id == cart.id,
                CartNeed.need_id == need.id,
                CartNeed.deleted.is_(None),
            )
            .scalar()
        )

        if cart_need is not None:
            raise HTTPException(600, 'Need already is in the cart')

        cart_need = CartNeed(need=need, cart=cart)
        session.add(cart_need)
        session.flush()
        session.expire(cart)
        return CartSchema.from_orm(cart)

    @authorize(USER)
    @json
    @commit
    @swag_from('./docs/cart/delete.yml')
    def delete(self):
        try:
            data = CartNeedInputSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        user_id = get_user_id()
        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
        cart_need = (
            session.query(CartNeed)
            .filter(
                CartNeed.cart_id == cart.id,
                CartNeed.need_id == data.need_id,
                CartNeed.deleted.is_(None),
            )
            .scalar()
        )

        if cart_need is None:
            raise HTTP_NOT_FOUND()

        cart_need.deleted = datetime.utcnow()
        session.flush()
        session.expire(cart)
        return CartSchema.from_orm(cart)


class CartPaymentAPI(Resource):
    @authorize(USER)
    @json
    @commit
    @swag_from('./docs/cart/payment.yml')
    def post(self):
        try:
            data = CartPaymentInSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        user_id = get_user_id()
        cart = (
            session.query(Cart).filter(Cart.user_id == user_id).with_for_update().one()
        )

        order_id = generate_order_id()
        if len(cart.needs) == 0:
            return HTTPException(600, 'Cart empty')

        total_amount = cart.total_amount + data.donation
        bank_amount = total_amount
        credit_amount = 0

        if data.use_credit:
            credit_amount = min(cart.user.credit, bank_amount)
            bank_amount -= credit_amount

            # Save some credit for the user to meet IPG minimum
            if bank_amount != 0 and bank_amount < configs.MIN_BANK_AMOUNT:
                extra_amount_needed = configs.MIN_BANK_AMOUNT - bank_amount
                credit_amount -= extra_amount_needed
                bank_amount += extra_amount_needed

        cart_payment = CartPayment(
            cart=cart,
            order_id=order_id,
            bank_amount=bank_amount,
            credit_amount=credit_amount,
            donation_amount=data.donation,
            needs_amount=cart.total_amount,
            total_amount=cart.total_amount + data.donation,
        )
        session.add(cart_payment)

        for cart_need in cart.needs:
            cart_payment.payments.append(
                Payment(
                    user=cart.user,
                    need=cart_need.need,
                    need_amount=cart_need.amount,
                    order_id=order_id,
                )
            )

        extra_paymnent = Payment(
            user=cart.user,
            donation_amount=data.donation,
            credit_amount=credit_amount,
            order_id=order_id,
            desc='Donation and credit payment',
        )
        cart_payment.payments.append(extra_paymnent)
        session.flush()

        if bank_amount == 0:
            cart_payment.verify()

            success_payment = render_template_i18n(
                'cart_successful_payment.html',
                cart_payment=cart_payment,
                locale=cart.user.locale,
            )
            return {'response': success_payment}, 299

        name = f'{cart.user.firstName} {cart.user.lastName}'
        callback = urljoin(configs.BASE_URL, 'api/v2/mycart/payment/verify')

        api_data = {
            'order_id': order_id,
            'amount': bank_amount,
            'name': name,
            'callback': callback,
        }

        transaction = idpay.new_transaction(**api_data)
        if 'error_code' in transaction:
            raise Exception(idpay.ERRORS[transaction['error_code']])

        cart_payment.gateway_payment_id = transaction['id']
        cart_payment.link = transaction['link']

        for payment in cart_payment.payments:
            payment.gateway_payment_id = cart_payment.gateway_payment_id
            payment.link = cart_payment.link

        session.flush()
        return CartPaymentSchema.from_orm(cart_payment)


class VerifyCartPayment(Resource):
    @staticmethod
    def _verify_payment(payment_id, order_id):
        unsuccessful_response = render_template_i18n(
            'unsuccessful_payment.html',
            locale=DEFAULT_LOCALE,
        )

        if not payment_id or not order_id:
            return make_response(unsuccessful_response)

        pending_payment = (
            session.query(CartPayment)
            .filter(
                CartPayment.gateway_payment_id == payment_id,
                CartPayment.order_id == order_id,
                CartPayment.verified.is_(None),
            )
            .with_for_update()
            .scalar()
        )

        if pending_payment is None:
            return make_response(unsuccessful_response)

        try:
            response = idpay.verify(
                pending_payment.gateway_payment_id,
                pending_payment.order_id,
            )
        except requests.exceptions.RequestException:
            return make_response(unsuccessful_response)

        if (
            not response
            or 'error_code' in response
            or response['status']
            not in (
                100,
                101,
                200,
            )
        ):
            return make_response(unsuccessful_response)

        transaction_date = datetime.fromtimestamp(int(response['date']))
        gateway_track_id = response['track_id']
        verified = datetime.fromtimestamp(int(response['verify']['date']))
        card_no = response['payment']['card_no']
        hashed_card_no = response['payment']['hashed_card_no']

        pending_payment.verify(
            transaction_date=transaction_date,
            track_id=gateway_track_id,
            verify_date=verified,
            card_no=card_no,
            hashed_card_no=hashed_card_no,
        )

        return make_response(
            render_template_i18n(
                'cart_successful_payment.html',
                cart_payment=pending_payment,
                locale=pending_payment.cart.user.locale,
            )
        )

    @json
    @commit
    def post(self):
        payment_id = request.form.get('id')
        order_id = request.form.get('order_id')
        return self._verify_payment(payment_id, order_id)

    @json
    @commit
    def get(self):
        payment_id = request.args.get('id')
        order_id = request.args.get('order_id')
        return self._verify_payment(payment_id, order_id)


api.add_resource(
    CartAPI,
    '/api/v2/mycart',
)

api.add_resource(
    CartNeedsAPI,
    '/api/v2/mycart/needs',
)

api.add_resource(
    CartPaymentAPI,
    '/api/v2/mycart/payment',
)

api.add_resource(VerifyCartPayment, '/api/v2/mycart/payment/verify')
