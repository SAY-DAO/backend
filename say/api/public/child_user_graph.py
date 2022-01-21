from flask_restful import Resource
from sqlalchemy.orm import selectinload

from say.api.ext import cache
from say.api.ext import limiter
from say.decorators import json
from say.models import Child
from say.models import Family
from say.schema.child_user_graph import ChildWithFamily

from ...orm import session
from .. import api
from .. import swag_from


class ChildUserGraph(Resource):
    decorators = [limiter.limit('15/minute')]

    @cache.cached(timeout=5 * 60)
    @json(ChildWithFamily, use_list=True)
    @swag_from('../docs/public/child_user_graph.yml')
    def get(self):
        children = (
            session.query(Child)
            .filter(
                Child.isDeleted.is_(False),
                Child.isMigrated.is_(False),
                Child.isConfirmed.is_(True),
                Child.existence_status == 1,
                Family.members_count > 0,
            )
            .join(Family, Family.id_child == Child.id)
            .options(selectinload('family'))
            .options(selectinload('family.current_members'))
            .options(selectinload('family.current_members.user'))
        )

        return children


api.add_resource(ChildUserGraph, '/api/v2/public/children')
