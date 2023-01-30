from flask import request
from flask_restful import Resource

from say.api import api
from say.api import swag_from
from say.authorization import authorize
from say.decorators import json
from say.decorators import query
from say.models import NeedStatusUpdate
from say.roles import ADMIN
from say.roles import SAY_SUPERVISOR
from say.roles import SUPER_ADMIN
from say.schema import NeedStatusUpdateSchema


class ListNeedStatusUpdates(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @query(
        NeedStatusUpdate,
        enable_filtering=True,
        filtering_schema=NeedStatusUpdateSchema,
        enable_pagination=True,
        enable_ordering=True,
        ordering_schema=NeedStatusUpdateSchema,
    )
    @json(NeedStatusUpdateSchema, use_list=True)
    @swag_from('./docs/need_status_update/list.yml')
    def get(self):
        return request._query


api.add_resource(
    ListNeedStatusUpdates,
    '/api/v2/need-status-updates',
)
