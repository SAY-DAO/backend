'''
Child APIs
'''


import collections
import functools
import os
from collections import OrderedDict
from datetime import datetime
from uuid import uuid4

import ujson
from flasgger import swag_from
from flask import request
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from flask_restful import abort
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import count
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import ARRAY
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.sql.sqltypes import String

from say import crud
from say.api.ext import api
from say.api.ext import logger
from say.authorization import authorize
from say.authorization import get_sw_ngo_id
from say.authorization import get_user_id
from say.authorization import get_user_role
from say.config import configs
from say.constants import DEFAULT_CHILD_ID
from say.decorators import json
from say.decorators import validate
from say.exceptions import HTTP_NOT_FOUND
from say.exceptions import HTTP_PERMISION_DENIED
from say.models import Child
from say.models import ChildNeed
from say.models import Family
from say.models import Invitation
from say.models import Need
from say.models import NeedFamily
from say.models import SocialWorker
from say.models import User
from say.models import UserFamily
from say.models import commit
from say.models import obj_to_dict
from say.orm import safe_commit
from say.orm import session
from say.roles import ADMIN
from say.roles import COORDINATOR
from say.roles import NGO_SUPERVISOR
from say.roles import SAY_SUPERVISOR
from say.roles import SOCIAL_WORKER
from say.roles import SUPER_ADMIN
from say.roles import USER
from say.schema.child import UserChildSchema
from say.schema.need import NeedSchema
from say.schema.need import NeedSummary
from say.schema.need import NeedSummaryQuery
from say.validations import valid_image_extension
from say.validations import valid_voice_extension


def filter_by_confirm(child_query, confirm):
    confirm = int(confirm)
    if confirm != 2:
        confirm = bool(confirm)
        return child_query.filter(Child.isConfirmed == confirm)

    return child_query


def filter_by_privilege(query, get=False):  # TODO: priv
    user_role = get_user_role()
    sw_id = get_user_id()
    ngo_id = get_sw_ngo_id()

    if user_role in [SOCIAL_WORKER, COORDINATOR]:
        if get:
            query = query.filter(
                or_(
                    Child.id_social_worker == sw_id,
                    Child.id == DEFAULT_CHILD_ID,
                )
            )
        else:
            query = query.filter_by(id_social_worker=sw_id)

    elif user_role in [NGO_SUPERVISOR]:
        if get:
            query = query.filter(
                or_(
                    Child.id_ngo == ngo_id,
                    Child.id == DEFAULT_CHILD_ID,
                )
            )
        else:
            query = query.filter(Child.id_ngo == ngo_id)

    elif user_role in [USER]:
        query = filter_by_user(query)

    return query


def filter_by_user(query):  # TODO: priv
    user_id = get_user_id()

    query = (
        query.join(Family)
        .join(UserFamily)
        .filter(UserFamily.id_user == user_id)
        .filter(UserFamily.isDeleted.is_(False))
    )
    return query


def filter_by_query(child_query):
    query = request.args

    ngo_id = query.get('ngo_id', None)
    sw_id = query.get('sw_id', None)

    if sw_id:
        child_query = child_query.filter_by(id_social_worker=sw_id)

    if ngo_id:
        child_query = child_query.filter_by(id_ngo=ngo_id)

    return child_query


def check_privileges(func_):  # TODO: priv
    @functools.wraps(func_)
    def wrapper(*args, **kwargs):
        query = request.args

        ngo_id = query.get('ngo_id', None)
        sw_id = query.get('sw_id', None)
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id or ngo_id:
                raise HTTP_PERMISION_DENIED()

        if sw_role in [NGO_SUPERVISOR]:
            if ngo_id:
                raise HTTP_PERMISION_DENIED()

        return func_(*args, **kwargs)

    return wrapper


class GetAllChildren(Resource):
    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @check_privileges
    @json
    @swag_from('./docs/child/all.yml')
    def get(self, confirm):
        query = request.args.copy()
        take = query.get('take', 100)
        skip = query.get('skip', 0)

        ex_status = query.get('existence_status', '1')

        confirm = int(confirm)
        children_query = (
            session.query(Child).filter_by(isDeleted=False).filter_by(isMigrated=False)
        )

        if ex_status.startswith('!'):
            children_query = children_query.filter(
                Child.existence_status != int(ex_status[1:])
            )
        else:
            children_query = children_query.filter(
                Child.existence_status == int(ex_status)
            )

        children_query = filter_by_privilege(children_query)
        children_query = filter_by_query(children_query)

        if int(confirm) == 0:
            children_query = children_query.filter_by(isConfirmed=False)
        elif int(confirm) == 1:
            children_query = children_query.filter_by(isConfirmed=True)

        children_query = children_query.order_by(Child.generatedCode.asc())

        children = children_query.offset(skip).limit(take)

        result = OrderedDict(
            totalCount=children_query.count(),
            children=[],
        )
        for child in children:
            result['children'].append(obj_to_dict(child))

        return result


class GetChildById(Resource):
    @authorize(
        USER,
        SOCIAL_WORKER,
        COORDINATOR,
        NGO_SUPERVISOR,
        SUPER_ADMIN,
        SAY_SUPERVISOR,
        ADMIN,
    )  # TODO: priv
    @json
    @swag_from('./docs/child/id.yml')
    def get(self, child_id, confirm):

        child_id = int(child_id)
        child_query = (
            session.query(Child)
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .filter(Child.id == child_id)
        )

        if child_id != DEFAULT_CHILD_ID:  # TODO: need needs
            child_query = filter_by_privilege(child_query)

        child_query = filter_by_confirm(child_query, confirm)

        child = child_query.one_or_none()
        if child is None:
            raise HTTP_NOT_FOUND()

        child_dict = obj_to_dict(child)
        child_dict['socialWorkerGeneratedCode'] = child.social_worker.generated_code

        if get_user_role() in [USER]:  # TODO: priv
            user_id = get_user_id()
            family_id = child.family.id

            user_role = (
                session.query(UserFamily.userRole)
                .filter_by(isDeleted=False)
                .filter_by(id_user=user_id)
                .filter_by(id_family=family_id)
                .one_or_none()
            )

            if user_role is None:
                raise HTTP_NOT_FOUND()

            # Unpack role
            (user_role,) = user_role

            child_family_members = [x for x in crud.child.get_family_members(child_id)]

            result = UserChildSchema(
                **child_dict,
                userRole=user_role,
                familyId=family_id,
                childFamilyMembers=child_family_members,
            )
            return result

        return child_dict


class GetChildByInvitationToken(Resource):
    @json
    @swag_from('./docs/child/get-by-token.yml')
    def get(self, token):
        try:
            user_id = get_user_id()
        except NoAuthorizationError:
            logger.info('random search: public')
            user_id = None
        except Exception as e:
            # Any other error
            logger.info('random search: bad jwt')
            logger.info(str(e))
            abort(403)

        invitation = (
            session.query(Invitation)
            .filter_by(token=token)
            .with_for_update()
            .one_or_none()
        )

        if not invitation:
            return {'messasge': 'Invitation not found'}, 400

        family = session.query(Family).get(invitation.family_id)

        if not family or family.child.isDeleted:
            return {'message': f'family {invitation.family_id} not found'}, 743

        child = (
            session.query(Child)
            .filter(Child.isDeleted.is_(False))
            .filter(Child.id == family.id_child)
            .options(selectinload('family.members.user'))
            .one_or_none()
        )

        if child is None:
            raise HTTP_NOT_FOUND()

        child_dict = obj_to_dict(child)
        child_dict['socialWorkerGeneratedCode'] = child.social_worker.generated_code
        child_dict['familyId'] = family.id
        child_dict['userRole'] = invitation.role

        if not user_id:
            child_dict['id'] = None

        child_family_members = [x for x in crud.child.get_family_members(child.id, True)]

        result = UserChildSchema(**child_dict, childFamilyMembers=child_family_members)
        return result


class GetChildNeeds(Resource):
    @authorize(
        USER,
        SOCIAL_WORKER,
        COORDINATOR,
        NGO_SUPERVISOR,
        SUPER_ADMIN,
        SAY_SUPERVISOR,
        ADMIN,
    )  # TODO: priv
    @json
    @swag_from('./docs/child/needs.yml')
    def get(self, child_id):
        child_id = int(child_id)
        child_query = (
            session.query(Child)
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .filter(Child.id == child_id)
        )
        if child_id != DEFAULT_CHILD_ID:  # TODO: need needs
            child_query = filter_by_privilege(child_query, get=True)

        child = child_query.one_or_none()
        if child is None:
            raise HTTP_NOT_FOUND()

        role = get_user_role()
        needs_query = (
            session.query(Need)
            .options(selectinload(Need.participants))
            .filter(
                Need.child_id == child_id,
                Need.isDeleted.is_(False),
                Need.isConfirmed.is_(True) if role == USER else True,
            )
            .order_by(Need.name)
        )

        needs = []
        for need in needs_query:
            need_dict = NeedSchema.from_orm(need)
            needs.append(need_dict.dict())

        result = dict(
            total_count=len(needs),
            needs=needs,
        )
        return result


# id, imageUrl, name, participants.user_avatar, progress, cost, isDone, isUrgent, category
class GetChildNeedsSummary(Resource):
    @authorize(
        USER,
        SOCIAL_WORKER,
        COORDINATOR,
        NGO_SUPERVISOR,
        SUPER_ADMIN,
        SAY_SUPERVISOR,
        ADMIN,
    )  # TODO: priv
    @validate(NeedSummaryQuery)
    @json
    @swag_from('./docs/child/needs_summary.yml')
    def get(self, child_id, data: NeedSummaryQuery):
        role = get_user_role()
        child_id = int(child_id)

        child_query = (
            session.query(Child)
            .filter(Child.isDeleted.is_(False))
            .filter(Child.isMigrated.is_(False))
            .filter(Child.id == child_id)
        )
        child_query = filter_by_privilege(child_query, get=True)

        child = child_query.one_or_none()
        if child is None:
            raise HTTP_NOT_FOUND()

        needs_query = (
            session.query(Need)
            .options(selectinload(Need.participants))
            .filter(
                Need.child_id == child_id,
                Need.isDeleted.is_(False),
                Need.isConfirmed.is_(True) if role == USER else True,
            )
            .order_by(Need.name, Need.doneAt)
        )

        if data.is_done:
            needs_query = needs_query.filter(Need.isDone.is_(data.is_done))

        if data.status:
            needs_query = needs_query.filter(Need.status == data.status)

        needs = []
        for need in needs_query:
            need_dict = NeedSummary.from_orm(need)
            needs.append(need_dict.dict())

        result = dict(
            total_count=len(needs),
            needs=needs,
        )
        return result


# TODO: ngo_id is needed?
class AddChild(Resource):
    def check_privilege(self, sw_id, ngo_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id() or ngo_id != get_sw_ngo_id():
                raise HTTP_PERMISION_DENIED()

        elif sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids or ngo_id != get_sw_ngo_id():
                raise HTTP_PERMISION_DENIED()

        elif sw_role in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
            if sw_id not in allowed_sw_ids:
                raise HTTP_PERMISION_DENIED()

        return

    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/child/add.yml')
    def post(self):
        ngo_id = int(request.form.get('ngo_id', get_sw_ngo_id()))
        sw_id = int(request.form.get('sw_id', get_user_id()))
        sw_role = get_user_role()

        allowed_sw_ids = []
        if sw_role in [NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN]:
            allowed_sw_ids_tuple = (
                session.query(SocialWorker.id)
                .filter_by(is_deleted=False)
                .filter_by(ngo_id=ngo_id)
                .distinct()
                .all()
            )

            allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

        # May throw 403
        self.check_privilege(sw_id, ngo_id, allowed_sw_ids)

        sw = (
            session.query(SocialWorker)
            .filter_by(id=sw_id)
            .filter_by(is_deleted=False)
            .one_or_none()
        )

        if sw is None:
            abort(403)

        code = sw.generated_code + format(sw.child_count + 1, '04d')

        if 'nationality' in request.form.keys():
            nationality = int(request.form['nationality'])
        else:
            nationality = None

        if 'housingStatus' in request.form.keys():
            housing_status = int(request.form['housingStatus'])
        else:
            housing_status = None

        if 'firstName_translations' in request.form.keys():
            first_name_translations = ujson.loads(
                request.form['firstName_translations'],
            )
        else:
            first_name_translations = None

        if 'lastName_translations' in request.form.keys():
            last_name_translations = ujson.loads(
                request.form['lastName_translations'],
            )
        else:
            last_name_translations = None

        if 'birthPlace' in request.form.keys():
            birth_place = request.form['birthPlace']
        else:
            birth_place = None

        if 'address' in request.form.keys():
            address = request.form['address']
        else:
            address = None

        if 'status' in request.form.keys():
            status = int(request.form['status'])
        else:
            status = None

        if 'education' in request.form.keys():
            education = int(request.form['education'])
        else:
            education = None

        if 'familyCount' in request.form.keys():
            family_count = int(request.form['familyCount'])
        else:
            family_count = None

        birth_date = datetime.strptime(request.form['birthDate'], '%Y-%m-%d')
        phone_number = request.form['phoneNumber']
        country = int(request.form['country'])
        city = int(request.form['city'])
        sayname_translations = ujson.loads(request.form['sayname_translations'])
        bio_translations = ujson.loads(request.form['bio_translations'])
        bio_summary_translations = ujson.loads(request.form['bio_summary_translations'])
        gender = True if request.form['gender'] == 'true' else False

        new_child = Child(
            phoneNumber=phone_number,
            nationality=nationality,
            awakeAvatarUrl='',
            sleptAvatarUrl='',
            housingStatus=housing_status,
            firstName_translations=first_name_translations,
            lastName_translations=last_name_translations,
            familyCount=family_count,
            education=education,
            birthPlace=birth_place,
            birthDate=birth_date,
            address=address,
            voiceUrl='',
            id_ngo=ngo_id,
            id_social_worker=sw_id,
            sayname_translations=sayname_translations,
            bio_translations=bio_translations,
            bio_summary_translations=bio_summary_translations,
            country=country,
            city=city,
            gender=gender,
            status=status,
            generatedCode=code,
        )

        session.add(new_child)
        session.flush()

        if (
            'voiceUrl' not in request.files
            or 'awakeAvatarUrl' not in request.files
            or 'sleptAvatarUrl' not in request.files
        ):
            return {'message': 'error occured in file uploading!'}, 400

        voice_file = request.files['voiceUrl']
        awake_avatar_file = request.files['awakeAvatarUrl']
        slpet_avatar_file = request.files['sleptAvatarUrl']

        child_path = os.path.join(
            configs.UPLOAD_FOLDER,
            str(new_child.id) + '-child',
        )

        if not os.path.isdir(child_path):
            os.makedirs(child_path, exist_ok=True)

        need_path = os.path.join(child_path, 'needs')
        if not os.path.isdir(need_path):
            os.makedirs(need_path, exist_ok=True)

        if extension := valid_voice_extension(voice_file):
            voice_name = uuid4().hex + extension
            new_child.voiceUrl = os.path.join(child_path, voice_name)
            voice_file.save(new_child.voiceUrl)
        else:
            return {'message': 'invalid voice file!'}, 400

        if extension := valid_image_extension(awake_avatar_file):
            awake_avatar_name = uuid4().hex + extension
            new_child.awakeAvatarUrl = os.path.join(child_path, awake_avatar_name)
            awake_avatar_file.save(new_child.awakeAvatarUrl)
        else:
            return {'message': 'invalid awake avatar file!'}, 400

        if extension := valid_image_extension(slpet_avatar_file):
            slept_avatar_name = uuid4().hex + extension
            new_child.sleptAvatarUrl = os.path.join(child_path, slept_avatar_name)
            slpet_avatar_file.save(new_child.sleptAvatarUrl)
        else:
            return {'message': 'invalid sleep avatar file!'}, 400

        safe_commit(session)
        return new_child


class UpdateChildById(Resource):
    def check_privilege(self, sw_id, ngo_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id() or ngo_id != get_sw_ngo_id():
                raise HTTP_PERMISION_DENIED()

        elif sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids or ngo_id != get_sw_ngo_id():
                raise HTTP_PERMISION_DENIED()

        return

    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/child/update.yml')
    def patch(self, child_id):
        sw_role = get_user_role()

        primary_child = (
            session.query(Child)
            .filter_by(id=child_id)
            .filter_by(isDeleted=False)
            .filter_by(isMigrated=False)
            .one_or_none()
        )
        if primary_child is None:
            abort(404)

        allowed_sw_ids = []
        if sw_role in [NGO_SUPERVISOR]:
            allowed_sw_ids_tuple = (
                session.query(SocialWorker.id)
                .filter_by(is_deleted=False)
                .filter_by(ngo_id=primary_child.id_ngo)
                .distinct()
                .all()
            )

            allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

        # May throw error
        self.check_privilege(
            primary_child.id_social_worker,
            primary_child.id_ngo,
            allowed_sw_ids,
        )

        child_path = os.path.join(
            configs.UPLOAD_FOLDER,
            str(primary_child.id) + '-child',
        )

        if not os.path.isdir(child_path):
            os.makedirs(child_path, exist_ok=True)

        need_path = os.path.join(child_path, 'needs')
        if not os.path.isdir(need_path):
            os.makedirs(need_path, exist_ok=True)

        if 'awakeAvatarUrl' in request.files.keys():
            awake_avatar_file = request.files['awakeAvatarUrl']
            if extension := valid_image_extension(awake_avatar_file):
                awake_avatar_name = uuid4().hex + extension

                temp_avatar_path = os.path.join(
                    configs.UPLOAD_FOLDER, str(primary_child.id) + '-child'
                )

                primary_child.awakeAvatarUrl = os.path.join(
                    temp_avatar_path,
                    str(primary_child.id) + awake_avatar_name,
                )

                awake_avatar_file.save(primary_child.awakeAvatarUrl)
            else:
                return {'message': 'invalid awake avatar file!'}, 400

        if 'sleptAvatarUrl' in request.files.keys():
            slept_avatar_file = request.files['sleptAvatarUrl']
            if extension := valid_image_extension(slept_avatar_file):
                slept_avatar_name = uuid4().hex + extension
                slept_avatar_path = os.path.join(
                    configs.UPLOAD_FOLDER, str(primary_child.id) + '-child'
                )

                primary_child.sleptAvatarUrl = os.path.join(
                    slept_avatar_path, slept_avatar_name
                )
                slept_avatar_file.save(primary_child.sleptAvatarUrl)
            else:
                return {'message': 'invalid slept avatar file!'}, 400

        if 'voiceUrl' in request.files.keys():
            voice_file = request.files['voiceUrl']
            if extension := valid_voice_extension(voice_file):
                voice_name = uuid4().hex + extension
                voice_path = os.path.join(
                    configs.UPLOAD_FOLDER,
                    str(primary_child.id) + '-child',
                )
                primary_child.voiceUrl = os.path.join(voice_path, voice_name)
                voice_file.save(primary_child.voiceUrl)
            else:
                return {'message': 'invalid voice file!'}, 400

        if 'phoneNumber' in request.form.keys():
            primary_child.phoneNumber = request.form['phoneNumber']

        if 'nationality' in request.form.keys():
            primary_child.nationality = int(request.form['nationality'])

        if 'housingStatus' in request.form.keys():
            primary_child.housingStatus = int(request.form['housingStatus'])

        if 'firstName_translations' in request.form.keys():
            primary_child.firstName_translations = ujson.loads(
                request.form['firstName_translations']
            )

        if 'lastName_translations' in request.form.keys():
            primary_child.lastName_translations = ujson.loads(
                request.form['lastName_translations']
            )

        if 'gender' in request.form.keys():
            primary_child.gender = True if request.form['gender'] == 'true' else False

        if 'familyCount' in request.form.keys():
            primary_child.familyCount = int(request.form['familyCount'])

        if 'country' in request.form.keys():
            primary_child.country = int(request.form['country'])

        if 'city' in request.form.keys():
            primary_child.city = int(request.form['city'])

        if 'status' in request.form.keys():
            primary_child.status = int(request.form['status'])

        if 'education' in request.form.keys():
            primary_child.education = int(request.form['education'])

        if 'birthPlace' in request.form.keys():
            primary_child.birthPlace = request.form['birthPlace']

        if 'birthDate' in request.form.keys():
            primary_child.birthDate = datetime.strptime(
                request.form['birthDate'], '%Y-%m-%d'
            )

        if 'address' in request.form.keys():
            primary_child.address = request.form['address']

        if 'bio' in request.form.keys():
            primary_child.bio = request.form['bio']

        if 'bio_summary' in request.form.keys():
            primary_child.bio_summary = request.form['bio_summary']

        if 'sayname_translations' in request.form.keys():
            primary_child.sayname_translations = ujson.loads(
                request.form['sayname_translations'],
            )

        if 'bio_translations' in request.form.keys():
            primary_child.bio_translations = ujson.loads(
                request.form['bio_translations'],
            )

        if 'bio_summary_translations' in request.form.keys():
            primary_child.bio_summary_translations = ujson.loads(
                request.form['bio_summary_translations'],
            )

        if 'existence_status' in request.form.keys():
            primary_child.existence_status = int(request.form['existence_status'])

            if primary_child.existence_status != 1:
                needs = session.query(Need).filter(
                    Need.isDeleted.is_(False),
                    Need.isConfirmed.is_(True),
                    Need.child_id == child_id,
                    Need.status <= 3,
                )

                for need in needs:
                    need.delete()

                primary_child.ngo.currentChildrenCount -= 1

        safe_commit(session)

        return primary_child


class DeleteChildById(Resource):
    def check_privilege(self, sw_id, ngo_id, allowed_sw_ids):  # TODO: priv
        sw_role = get_user_role()

        if sw_role in [SOCIAL_WORKER, COORDINATOR]:
            if sw_id != get_user_id() or ngo_id != get_sw_ngo_id():
                raise HTTP_PERMISION_DENIED()

        if sw_role in [NGO_SUPERVISOR]:
            if sw_id not in allowed_sw_ids or ngo_id != get_sw_ngo_id():
                raise HTTP_PERMISION_DENIED()
        return

    @authorize(
        SOCIAL_WORKER, COORDINATOR, NGO_SUPERVISOR, SUPER_ADMIN, SAY_SUPERVISOR, ADMIN
    )  # TODO: priv
    @json
    @swag_from('./docs/child/delete.yml')
    def patch(self, child_id):
        sw_role = get_user_role()

        child = (
            session.query(Child)
            .filter_by(id=child_id)
            .filter_by(isDeleted=False)
            .filter_by(isMigrated=False)
            .one_or_none()
        )
        if child is None:
            abort(404)

        allowed_sw_ids = []
        if sw_role in [NGO_SUPERVISOR]:
            allowed_sw_ids_tuple = (
                session.query(SocialWorker.id)
                .filter_by(is_deleted=False)
                .filter_by(id_ngo=child.id_ngo)
                .distinct()
                .all()
            )

            allowed_sw_ids = [item[0] for item in allowed_sw_ids_tuple]

        # May throw error
        self.check_privilege(
            child.id_social_worker,
            child.id_ngo,
            allowed_sw_ids,
        )

        if child.isConfirmed:
            return {'message': 'error: confirmed child cannot be deleted!'}, 400

        family = (
            session.query(Family)
            .filter_by(isDeleted=False)
            .filter_by(id_child=child_id)
            .first()
        )
        needs = (
            session.query(ChildNeed)
            .filter_by(isDeleted=False)
            .filter_by(id_child=child_id)
        )

        for need in needs:
            need.isDeleted = True

        child.isDeleted = True

        if family:
            family.isDeleted = True

        child.social_worker.currentChildCount -= 1
        child.ngo.currentChildrenCount -= 1

        safe_commit(session)

        return {'message': 'child deleted successfully!'}


class ConfirmChild(Resource):
    @authorize(SUPER_ADMIN, SAY_SUPERVISOR, ADMIN)  # TODO: priv
    @json
    @commit
    @swag_from('./docs/child/confirm.yml')
    def patch(self, child_id):
        social_worker_id = get_user_id()

        child = (
            session.query(Child)
            .filter_by(id=child_id)
            .filter_by(isDeleted=False)
            .filter_by(isMigrated=False)
            .one_or_none()
        )

        if not child:
            return {'message': 'not found'}, 404

        if child.isConfirmed:
            return {'message': 'child has already confirmed!'}, 400

        child.isConfirmed = True
        child.confirmUser = social_worker_id
        child.confirmDate = datetime.utcnow()
        child.ngo.currentChildrenCount += 1

        new_family = Family(id_child=child.id)
        session.add(new_family)

        return {'message': 'child confirmed successfully!'}


class MigrateChild(Resource):
    @authorize(SUPER_ADMIN, ADMIN, SAY_SUPERVISOR)  # TODO: priv
    @json
    @swag_from('./docs/child/migrate.yml')
    def patch(self, child_id):
        new_sw_id = request.form.get('new_sw_id', None)

        if not new_sw_id:
            return {'message': 'new_sw_id can not be null'}, 422

        try:
            new_sw_id = int(new_sw_id)
        except (ValueError, TypeError):
            return {'message': 'Invalid new_sw_id'}, 422

        new_sw = (
            session.query(SocialWorker)
            .filter_by(is_deleted=False)
            .filter_by(id=new_sw_id)
            .with_for_update()
            .one_or_none()
        )

        if not new_sw:
            return {'message': 'social_worker not found'}, 422

        child = (
            session.query(Child)
            .filter_by(id=child_id)
            .filter_by(isDeleted=False)
            .with_for_update()
            .one_or_none()
        )

        if not child:
            return {'message': 'Child not found'}, 404

        old_sw = child.social_worker
        if old_sw.id == new_sw_id:
            return {'message': 'Can not migrate to same sw'}, 422

        child.migrate(new_sw)
        safe_commit(session)

        return {'message': 'child migrated successfully!'}


class GetActiveChildrenApi(Resource):
    @authorize(SUPER_ADMIN, ADMIN, SAY_SUPERVISOR)  # TODO: priv
    @json
    @commit
    @swag_from('./docs/child/active-children.yml')
    def get(self):
        return Child.get_actives().order_by(Child.created)


api.add_resource(GetActiveChildrenApi, '/api/v2/child/actives')
api.add_resource(GetChildById, '/api/v2/child/childId=<child_id>&confirm=<confirm>')
api.add_resource(
    GetChildByInvitationToken,
    '/api/v2/child/invitations/<token>',
)
api.add_resource(GetChildNeeds, '/api/v2/child/childId=<child_id>/needs')
api.add_resource(GetChildNeedsSummary, '/api/v2/child/<child_id>/needs/summary')
api.add_resource(GetAllChildren, '/api/v2/child/all/confirm=<confirm>')
api.add_resource(
    AddChild,
    '/api/v2/child/add/',
)
api.add_resource(UpdateChildById, '/api/v2/child/update/childId=<child_id>')
api.add_resource(DeleteChildById, '/api/v2/child/delete/childId=<child_id>')
api.add_resource(
    ConfirmChild,
    '/api/v2/child/confirm/childId=<child_id>',
)
api.add_resource(
    MigrateChild,
    '/api/v2/child/migrate/childId=<child_id>',
)
