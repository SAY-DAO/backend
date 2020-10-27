from flask_restful import Resource
from sqlalchemy import func

from .. import swag_from, api
from say.orm import obj_to_dict
from say.models import Need, Child, session
from say.decorators import json


class RandomNeed(Resource):

    @json
    @swag_from('../docs/public/random_need.yml')
    def get(self):
        need = session.query(
            Need.id, 
            Need.name, 
            Need.imageUrl,
            Need.cost, 
            Child.awakeAvatarUrl, 
            Child.sayName,
            Need.type,
            Need.link,
            Need.img,
        ).filter(
            Need.status.in_([0, 1]),
            Need.name.isnot(None),
            Need.isConfirmed.is_(True),
            Child.isConfirmed.is_(True),
        ).join(
            Child, 
            Child.id == Need.child_id,
        ) \
            .order_by(func.random()) \
            .limit(1) \
            .first()

        return dict(
            id=need[0],
            name=need[1],
            imageUrl=need[2],
            cost=need[3],
            childAvatarUrl=need[4],
            childSayName=need[5],
            type=need[6],
            retailerLink=need[7],
            retailerImage=need[8],
        )


api.add_resource(RandomNeed, '/api/v2/public/random/need')
