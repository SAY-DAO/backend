from datetime import date
from datetime import datetime
from typing import cast
from urllib.parse import urljoin

from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.api.ext import api
from say.api.payment_api import generate_order_id
from say.authorization import authorize
from say.authorization import get_user_id
from say.config import configs
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.exceptions import HTTPException
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
from say.schema.cart import CartSchema

from .ext import idpay


class CartAPI(Resource):
    @authorize(USER)
    @json
    @swag_from('./docs/cart/get.yml')
    def get(self):
        user_id = get_user_id()
        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
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
        need = session.query(Need) \
            .join(Child) \
            .join(Family) \
            .join(UserFamily) \
            .filter(
                Need.id == data.need_id,
                Need.isDeleted.is_(False),
                Need.isConfirmed.is_(True),
                Need.unpayable.is_(False),
                Need.isDone.is_(False),
                UserFamily.id_user == user_id,
                UserFamily.isDeleted.is_(False),
            ).one_or_none()

        if need is None:
            raise HTTPException(400, f'Can not add need {data.need_id} to cart')

        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
        cart_need = session.query(CartNeed).filter(
            CartNeed.cart_id == cart.id,
            CartNeed.need_id == need.id,
            CartNeed.deleted.is_(None),
        ).scalar()

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
        cart_need = session.query(CartNeed).filter(
            CartNeed.cart_id == cart.id,
            CartNeed.need_id == data.need_id,
            CartNeed.deleted.is_(None),
        ).scalar()

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
        cart = session.query(Cart).filter(
            Cart.user_id == user_id
        ).with_for_update().one()

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
            cart_payment.payments.append(Payment(
                user=cart.user,
                need=cart_need.need,
                need_amount=cart_need.amount,
                order_id=order_id,
            ))

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
