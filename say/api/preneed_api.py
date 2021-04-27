from flasgger import swag_from
from flask_restful import Resource

from say.api.ext import api
from say.authorization import authorize
from say.constants import DEFAULT_CHILD_ID
from say.decorators import json
from say.models import Need
from say.models import commit
from say.orm import session
from say.roles import *
from say.schema.preneed import PreneedSummarySchema


class PreNeedsAPi(Resource):

    @authorize(SOCIAL_WORKER, NGO_SUPERVISOR, ADMIN, SUPER_ADMIN)
    @json
    @swag_from('./docs/preneed/list.yml')
    def get(self):
        preneeds = session.query(
            Need.id,
            Need.name.label('name'),
            Need.cost,
            Need.title,
        ) \
            .filter(
                Need.child_id == DEFAULT_CHILD_ID,
                Need.isDeleted == False,    
            )

        return PreneedSummarySchema.from_query_list(preneeds)


api.add_resource(
    PreNeedsAPi,
    '/api/v2/preneeds/',
)
