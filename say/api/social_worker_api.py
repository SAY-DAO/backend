from flasgger import swag_from
from flask import request
from flask_restful import Resource
from sqlalchemy.orm import selectinload

from say.models import Child
from say.models import City
from say.models import Need
from say.models import Ngo
from say.models import commit
from say.models.social_worker_model import SocialWorker
from say.orm import safe_commit
from say.orm import session
from say.schema.child_migration import ChildMigrationSchema

from ..authorization import authorize
from ..authorization import get_sw_ngo_id
from ..authorization import get_user_id
from ..authorization import get_user_role
from ..decorators import get_skip_take
from ..decorators import json
from ..decorators import query
from ..decorators import validate
from ..exceptions import HTTP_BAD_REQUEST
from ..exceptions import HTTP_NOT_FOUND
from ..exceptions import HTTP_PERMISION_DENIED
from ..roles import ADMIN
from ..roles import COORDINATOR
from ..roles import NGO_SUPERVISOR
from ..roles import SAY_SUPERVISOR
from ..roles import SOCIAL_WORKER
from ..roles import SUPER_ADMIN
from ..schema.social_worker import MigrateSocialWorkerChildrenSchema
from ..schema.social_worker import MyPagePaginationSchema
from ..schema.social_worker import MyPageQuerySchema
from ..schema.social_worker import NewSocialWorkerSchema
from ..schema.social_worker import SocialWorkerMyPageSchema
from ..schema.social_worker import SocialWorkerSchema
from ..schema.social_worker import UpdateSocialWorkerSchema
from .ext import api


'''
Social Worker APIs
'''


def filter_by_role(query, user):
    if user.type_name not in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR]:  # TODO: priv
        if user.type_name not in (NGO_SUPERVISOR, COORDINATOR):
            query = query.filter(SocialWorker.id == user.id)

        query = query.filter(SocialWorker.ngo_id == user.ngo_id)

    return query


def filter_by_privilege(query):
    return filter_by_role(query, request.user)


class ListCreateSocialWorkers(Resource):
    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @query(
        SocialWorker,
        SocialWorker.is_deleted.is_(False),
        filter_callbacks=[filter_by_privilege],
        enable_filtering=True,
        filtering_schema=SocialWorkerSchema,
        enable_pagination=True,
        enable_ordering=True,
        ordering_schema=SocialWorkerSchema,
    )
    @json(SocialWorkerSchema, use_list=True)
    @swag_from('./docs/social_worker/all.yml')
    def get(self):
        return request._query

    @authorize(SUPER_ADMIN, ADMIN, SAY_SUPERVISOR)  # TODO: priv
    @validate(NewSocialWorkerSchema)
    @json(SocialWorkerSchema)
    @swag_from('./docs/social_worker/add.yml')
    def post(self, data: NewSocialWorkerSchema):
        ngo = (
            session.query(Ngo)
            .filter(
                Ngo.isDeleted.is_(False),
                Ngo.id == data.ngo_id,
            )
            .populate_existing()
            .with_for_update()
            .one_or_none()
        )

        if ngo is None:
            raise HTTP_BAD_REQUEST(message='NGO not found')

        if data.city_id:
            city = (
                session.query(City)
                .filter(
                    City.id == data.city_id,
                )
                .populate_existing()
                .with_for_update()
                .one_or_none()
            )

            if city is None:
                raise HTTP_BAD_REQUEST(message='city not found')

        generated_code = format(data.ngo_id, '03d') + format(
            ngo.socialWorkerCount + 1,
            '03d',
        )

        username = f'sw{generated_code}'
        password = SocialWorker.generate_password()

        new_social_worker = SocialWorker(
            username=username,
            password=password,
            generated_code=generated_code,
            **data.dict(),
        )

        session.add(new_social_worker)
        safe_commit(session)
        new_social_worker.send_password(password=password)
        return new_social_worker


class GetUpdateDeleteSocialWorkers(Resource):
    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN, SOCIAL_WORKER)  # TODO: priv
    @query(
        SocialWorker,
        SocialWorker.is_deleted.is_(False),
        filter_callbacks=[filter_by_privilege],
    )
    @json(SocialWorkerSchema)
    @swag_from('./docs/social_worker/id.yml')
    def get(self, id):
        social_worker = request._query.filter(SocialWorker.id == id).one_or_none()

        if not social_worker:
            raise HTTP_NOT_FOUND()

        return social_worker

    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @validate(UpdateSocialWorkerSchema)
    @json(SocialWorkerSchema)
    @commit
    @swag_from('./docs/social_worker/update.yml')
    def patch(self, id, data: UpdateSocialWorkerSchema):
        role = get_user_role()
        sw: SocialWorker = (
            session.query(SocialWorker)
            .filter_by(id=id)
            .filter_by(is_deleted=False)
            .with_for_update()
        )
        if data.ngo_id:
            sw.options(selectinload(SocialWorker.children))

        sw = sw.one_or_none()
        if sw is None:
            raise HTTP_NOT_FOUND()

        if role in [COORDINATOR, NGO_SUPERVISOR]:  # TODO: priv
            user_id = get_user_id()
            user = session.query(SocialWorker).get(user_id)
            if user is None or user.ngo_id != sw.ngo_id:
                raise HTTP_PERMISION_DENIED()

        if data.ngo_id is not None:
            if role not in {SUPER_ADMIN, ADMIN, SAY_SUPERVISOR}:
                raise HTTP_PERMISION_DENIED()

            if data.ngo_id != sw.ngo_id:
                new_ngo = (
                    session.query(Ngo.id)
                    .filter(
                        Ngo.id == data.ngo_id,
                        Ngo.isDeleted.is_(False),
                    )
                    .one_or_none()
                )

                if new_ngo is None:
                    raise HTTP_BAD_REQUEST(message='NGO not found')

                sw.change_ngo(data.ngo_id)

        if data.city_id:
            city = (
                session.query(City)
                .filter(
                    City.id == data.city_id,
                )
                .populate_existing()
                .with_for_update()
                .one_or_none()
            )

            if city is None:
                raise HTTP_BAD_REQUEST(message='city not found')

        sw.update_from_schema(data)
        # Password is protected and secret and needs to be set manually
        if data.password is not None:
            sw.password = data.password.get_secret_value()

        return sw

    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @query(
        SocialWorker,
        SocialWorker.is_deleted.is_(False),
    )
    @json(SocialWorkerSchema)
    @commit
    @swag_from('./docs/social_worker/delete.yml')
    def delete(self, id):
        sw = request._query.filter(SocialWorker.id == id).with_for_update().one_or_none()
        if sw is None:
            raise HTTP_NOT_FOUND()

        if sw.is_deleted:
            raise HTTP_BAD_REQUEST(message='Social Worker already deleted')

        has_active_child = (
            session.query(Child.id)
            .filter(Child.id_social_worker == id)
            .filter(Child.isConfirmed.is_(True))
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .count()
        )

        if has_active_child:
            raise HTTP_BAD_REQUEST(
                message=f'Social worker {id} has active' f' children and can not deactivate'
            )

        sw.is_deleted = True
        return sw


class DeactivateSocialWorker(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @query(
        SocialWorker,
        SocialWorker.is_deleted.is_(False),
    )
    @json(SocialWorkerSchema)
    @commit
    @swag_from('./docs/social_worker/deactivate.yml')
    def post(self, id):
        sw = request._query.filter_by(id=id).with_for_update().one_or_none()

        if not sw:
            raise HTTP_NOT_FOUND()

        if not sw.is_active:
            raise HTTP_BAD_REQUEST(message='social worker already deactivated')

        has_active_child = (
            session.query(Child.id)
            .filter(Child.id_social_worker == id)
            .filter(Child.isConfirmed.is_(True))
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .count()
        )

        if has_active_child:
            raise HTTP_BAD_REQUEST(
                message=f'Social worker {id} has active' f' children and can not deactivate'
            )

        sw.deactivate()
        return sw


class ActivateSocialWorker(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @query(
        SocialWorker,
        SocialWorker.is_deleted.is_(False),
    )
    @json(SocialWorkerSchema)
    @commit
    @swag_from('./docs/social_worker/activate.yml')
    def post(self, id):
        sw = request._query.filter_by(id=id).filter_by(is_deleted=False).one_or_none()
        if not sw:
            raise HTTP_NOT_FOUND()

        if sw.is_active:
            raise HTTP_BAD_REQUEST(message='social worker already activated')

        sw.activate()
        return sw


class MigrateSocialWorkerChildren(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @validate(MigrateSocialWorkerChildrenSchema)
    @query(
        SocialWorker,
        SocialWorker.is_deleted.is_(False),
        SocialWorker.is_active.is_(True),
    )
    @json(ChildMigrationSchema, use_list=True)
    @commit
    @swag_from('./docs/social_worker/migrate_children.yml')
    def post(self, id, data):
        if data.destination_social_worker_id == id:
            raise HTTP_BAD_REQUEST(message='destination social worker is same as source')

        sw = request._query.filter(SocialWorker.id == id).with_for_update().one_or_none()

        if not sw:
            raise HTTP_NOT_FOUND()

        destination_sw = (
            session.query(SocialWorker)
            .filter(SocialWorker.id == data.destination_social_worker_id)
            .filter(SocialWorker.is_deleted.is_(False))
            .filter(SocialWorker.is_active.is_(True))
            .with_for_update()
            .one_or_none()
        )

        if not destination_sw:
            raise HTTP_BAD_REQUEST(message='destination social worker not found')

        children = (
            session.query(Child)
            .filter(Child.id_social_worker == id)
            .filter(Child.isDeleted.is_(False))
            .with_for_update()
        )

        resp = []
        for child in children:
            migration = child.migrate(destination_sw)
            resp.append(migration)

        return resp


class SocialWorkerCreatedNeeds(Resource):
    def filter_by_sw(query):
        user = request.user
        sw_id = request.view_args.get('id', -1)

        social_worker = (
            session.query(SocialWorker)
            .filter(
                SocialWorker.id == sw_id,
                SocialWorker.is_deleted.is_(False),
            )
            .one_or_none()
        )

        if not social_worker:
            raise HTTP_NOT_FOUND()

        query = query.filter(Need.created_by_id == sw_id)

        if user.type_name not in [SUPER_ADMIN, ADMIN, SAY_SUPERVISOR]:  # TODO: priv
            query = query.join(SocialWorker, SocialWorker.id == Need.created_by_id)

            if user.type_name not in (NGO_SUPERVISOR, COORDINATOR) and sw_id != user.id:
                raise HTTP_PERMISION_DENIED()

            if user.ngo_id != social_worker.ngo_id:
                raise HTTP_PERMISION_DENIED()

            query = query.filter(SocialWorker.ngo_id == user.ngo_id)

        return query

    @authorize(COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN, SOCIAL_WORKER)  # TODO: priv
    @query(
        Need,
        Need.isDeleted.is_(False),
        filter_callbacks=[filter_by_sw],
        enable_pagination=True,
    )
    @json
    @swag_from('./docs/social_worker/created_needs.yml')
    def get(self, id):
        return request._query


class SocialWorkerMyPage(Resource):
    @authorize(
        COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN, SOCIAL_WORKER
    )  # TODO: priv
    @validate(MyPageQuerySchema)
    @json(SocialWorkerMyPageSchema, use_list=True)
    @swag_from('./docs/social_worker/my_page.yml')
    def get(self, data: MyPageQuerySchema):
        take, skip = get_skip_take(request, MyPagePaginationSchema)
        user_role = get_user_role()
        ngo_id = get_sw_ngo_id()
        sw_id = get_user_id()

        query = session.query(Child).filter(
            Child.isDeleted.is_(False),
            Child.existence_status == 1,
            Child.isMigrated.is_(False),
        )

        if data.sw_id:
            query = query.filter(Child.id_social_worker == data.sw_id)

        if user_role in [SOCIAL_WORKER, COORDINATOR]:
            query = query.filter(Child.id_social_worker == sw_id)
        elif user_role in [NGO_SUPERVISOR]:
            query = query.filter(Child.id_ngo == ngo_id)

        children_query = (
            query.options(
                selectinload(Child.needs).selectinload(Need.verified_payments),
                selectinload(Child.needs).selectinload(Need.receipts_),
                selectinload(Child.needs).selectinload(Need.participants),
                selectinload(Child.needs).selectinload(Need.status_updates),
            )
            .order_by(Child.created.desc())
            .limit(take)
            .offset(skip)
        )

        return children_query


api.add_resource(
    ListCreateSocialWorkers,
    '/api/v2/socialworkers/',
    '/api/v2/socialworkers',
)

api.add_resource(
    GetUpdateDeleteSocialWorkers,
    '/api/v2/socialworkers/<int:id>',
)

api.add_resource(
    DeactivateSocialWorker,
    '/api/v2/socialworkers/<int:id>/deactivate',
)
api.add_resource(
    ActivateSocialWorker,
    '/api/v2/socialworkers/<int:id>/activate',
)

api.add_resource(
    MigrateSocialWorkerChildren,
    '/api/v2/socialworkers/<int:id>/children/migrate',
)

api.add_resource(
    SocialWorkerCreatedNeeds,
    '/api/v2/socialworkers/<int:id>/createdNeeds',
)

api.add_resource(
    SocialWorkerMyPage,
    '/api/v2/socialworkers/my-page',
)
