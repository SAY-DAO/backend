from datetime import date
from datetime import datetime

from dotenv.main import dotenv_values
from flasgger import swag_from
from flask import request
from flask_restful import Resource

from say.api.ext import api
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
from say.models import UserFamily
from say.models import commit
from say.orm import obj_to_dict
from say.orm import session
from say.roles import USER
from say.schema.cart import CartNeedDeleteSchema
from say.schema.cart import CartNeedInputSchema
from say.schema.cart import CartSchema


class CartAPI(Resource):
    @authorize(USER)
    @json
    @swag_from('./docs/cart/get.yml')
    def get(self):
        user_id = get_user_id()
        cart = session.query(Cart).filter(Cart.user_id == user_id).one()
        return cart.needs


class CartNeedsAPI(Resource):
    @authorize(USER)
    @json
    @commit
    @swag_from('./docs/cart/put.yml')
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
            ).one_or_none()

        if need is None:
            raise HTTPException(400, f'Can not add need {data.need_id} to cart')

        cart = session.query(Cart).filter(Cart.user_id == user_id).one()

        cart_need = session.query(CartNeed).filter(
            CartNeed.cart_id == cart.id,
            CartNeed.need_id == need.id,
            CartNeed.deleted.is_(None),
        ).scalar()

        if cart_need is None:
            cart_need = CartNeed(need=need, cart=cart)
            session.add(cart_need)

        max_need_amount = need.cost - need.paid
        if data.amount is None or data.amount > max_need_amount:
            data.amount = max_need_amount

        remaining_amount = max_need_amount - data.amount
        if remaining_amount != 0 and remaining_amount < configs.MIN_BANK_AMOUNT:
            raise HTTPException(
                600,
                f'Amount should be equal to {max_need_amount} or less than {remaining_amount}',
            )

        cart_need.amount = data.amount
        cart_need.donation = data.donation
        session.flush()
        session.expire(cart)
        return CartSchema.from_orm(cart)

    @authorize(USER)
    @json
    @commit
    @swag_from('./docs/cart/delete.yml')
    def delete(self):
        try:
            data = CartNeedDeleteSchema(**request.form.to_dict())
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


api.add_resource(
    CartAPI,
    '/api/v2/mycart',
)

api.add_resource(
    CartNeedsAPI,
    '/api/v2/mycart/needs',
)
