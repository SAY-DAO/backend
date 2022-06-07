from flasgger import swag_from
from flask import request
from flask_restful import Resource
from sqlalchemy_continuum import version_class

from say.authorization import authorize
from say.decorators import json
from say.decorators import query
from say.models import Need
from say.roles import ADMIN
from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SAY_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from say.schema import NeedSchema

from ..ext import api


NeedVersion = version_class(Need)


class ListNeedVersions(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @query(
        NeedVersion,
        enbale_filtering=True,
        filtering_schema=NeedSchema,
        enable_pagination=True,
        enable_ordering=True,
        ordering_schema=NeedSchema,
    )
    @json(NeedSchema, use_list=True)
    @swag_from('../docs/need/list_versions.yml')
    def get(self):
        print(Need.versions)
        return request._query


api.add_resource(
    ListNeedVersions,
    '/api/v2/needs/versions',
)
