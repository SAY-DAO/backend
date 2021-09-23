from urllib.parse import urljoin

from flask_restful import Resource
from sqlalchemy import func

from say.config import configs
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.locale import LANGS
from say.locale import ChangeLocaleTo
from say.models import Child
from say.models import Need
from say.orm import session

from ...orm import session
from .. import api
from .. import swag_from


class RandomNeed(Resource):
    @json
    @swag_from('../docs/public/random_need.yml')
    def get(self):
        need = (
            session.query(
                Need.id,
                Need.name,
                Need.imageUrl,
                Need.cost,
                Child.avatarUrl,
                Child.sayName,
                Need.type,
                Need.link,
                Need.img,
                Need.description,
            )
            .filter(
                Need.status.in_([0, 1]),
                Need.name.isnot(None),
                Need.isConfirmed.is_(True),
                Need.isDeleted.is_(False),
                Child.isConfirmed.is_(True),
            )
            .join(
                Child,
                Child.id == Need.child_id,
            )
            .order_by(func.random())
            .limit(1)
            .first()
        )

        return dict(
            id=need[0],
            name=need[1],
            image=urljoin(configs.BASE_URL, need[2]),
            cost=need[3],
            childAvatarUrl=urljoin(configs.BASE_URL, need[4]),
            childSayName=need[5],
            type=need[6],
            retailerLink=need[7],
            retailerImage=need[8],
            description=need[9],
        )


api.add_resource(RandomNeed, '/api/v2/public/random/need')
