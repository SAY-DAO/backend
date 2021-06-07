from urllib.parse import urljoin

from flask_restful import Resource

from say.config import configs
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.locale import LANGS
from say.locale import ChangeLocaleTo
from say.models import Child
from say.models import Need

from ...orm import session
from .. import api
from .. import swag_from


class PublicNeed(Resource):

    @json
    @swag_from('../docs/public/get_need.yml')
    def get(self, id):
        with ChangeLocaleTo(LANGS.en):
            need = session.query(
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
            ).filter(
                Need.id == id,
                Need.isDeleted.is_(False),
            ).join(
                Child,
                Child.id == Need.child_id,
            ).one_or_none()

        if not need:
            raise HTTP_NOT_FOUND()

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


api.add_resource(PublicNeed, '/api/v2/public/needs/<int:id>')
