from . import *
from say.models import commit, session
from say.models import Need, SocialWorker, ChangeCost, ChangeCostStatus, Child, \
    ChangeCostCreateSchema, ChangeCostRejectSchema, ChangeCostAcceptSchema


def get_need(need_id):
    sw_id = get_user_id()
    ngo_id = get_sw_ngo_id()
    sw_role = get_user_role()

    need_query = session.query(Need) \
        .filter(Need.id == need_id) \
        .filter(Need.isDeleted == False) \
        .filter(Need.isConfirmed == True)

    if sw_role == SOCIAL_WORKER:
        need_query \
            .join(Child, Child.id == Need.child_id) \
            .filter(Child.id_social_worker == sw_id)

    elif sw_role == NGO_SUPERVISOR:
        need_query \
            .join(Child, Child.id == Need.child_id) \
            .filter(Child.id_ngo == ngo_id)

    return need_query


class ChangeCostAPi(Resource):

    @authorize(SOCIAL_WORKER, NGO_SUPERVISOR, ADMIN, SUPER_ADMIN)
    @json
    @swag_from('./docs/change_cost/list_for_need.yml')
    def get(self, need_id):
        sw_id = get_user_id()

        need = get_need(need_id).one_or_none()
        if not need:
            return HTTP_NOT_FOUND()

        change_costs = session.query(ChangeCost) \
            .filter_by(
                need_id = need.id,
            )

        return change_costs

    @authorize(SOCIAL_WORKER, NGO_SUPERVISOR, ADMIN, SUPER_ADMIN)
    @json
    @commit
    @swag_from('./docs/change_cost/create.yml')
    def put(self, need_id):
        try:
            form_data = ChangeCostCreateSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        sw_id = get_user_id()
        to = form_data.to
        description = form_data.description

        need = get_need(need_id).one_or_none()
        if not need:
            return HTTP_NOT_FOUND()

        change_cost = session.query(ChangeCost) \
            .filter_by(
                status = ChangeCostStatus.pending,
                need_id = need.id,
            ).one_or_none()

        if not change_cost:
            change_cost = ChangeCost(
                need_id=need.id,
            )
            session.add(change_cost)

        change_cost.from_ = need.cost
        change_cost.requester_id = sw_id
        change_cost.to = to
        change_cost.description = description,

        return change_cost


class ChangeCostRejectApi(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @json
    @commit
    @swag_from('./docs/change_cost/reject.yml')
    def post(self, need_id, id):
        try:
            data = ChangeCostRejectSchema(**request.form.to_dict())
        except ValueError as e:
            return e.json(), 400

        need = get_need(need_id).one_or_none()
        if not need:
            return HTTP_NOT_FOUND()

        change_cost = session.query(ChangeCost) \
            .filter(
                ChangeCost.id == id,
                ChangeCost.status.in_([
                    ChangeCostStatus.pending,
                    ChangeCostStatus.rejected,
                ]),
            ).one_or_none()

        if not change_cost:
            return HTTP_NOT_FOUND()

        change_cost.status = ChangeCostStatus.rejected
        sw_id = get_user_id()
        change_cost.reviewer_id = sw_id
        change_cost.reject_cause = data.rejectCause

        return change_cost


class ChangeCostAcceptApi(Resource):
    @authorize(ADMIN, SUPER_ADMIN)
    @json
    @commit
    @swag_from('./docs/change_cost/accept.yml')
    def post(self, need_id, id):
        sw_id = get_user_id()
        try:
            data = ChangeCostAcceptSchema(
                status=ChangeCostStatus.accepted,
                reviewer_id=sw_id,
                **request.form.to_dict(),
            )
        except ValueError as e:
            return e.json(), 400

        need = get_need(need_id).one_or_none()
        if not need:
            return HTTP_NOT_FOUND()

        change_cost = session.query(ChangeCost) \
            .filter(
                ChangeCost.id == id,
                ChangeCost.status.in_([
                    ChangeCostStatus.pending,
                ]),
            ).one_or_none()

        if not change_cost:
            return HTTP_NOT_FOUND()

        change_cost.update(**data.dict(exclude_unset=True))
        return change_cost


api.add_resource(
    ChangeCostAPi,
    '/api/v2/need/<int:need_id>/change_cost',
)

api.add_resource(
    ChangeCostRejectApi,
    '/api/v2/need/<int:need_id>/change_cost/<id>/reject',
)

api.add_resource(
    ChangeCostAcceptApi,
    '/api/v2/need/<int:need_id>/change_cost/<id>/accept',
)

