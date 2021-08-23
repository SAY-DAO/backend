import os
from datetime import datetime
from typing import Any
from typing import Optional
from urllib.parse import urljoin
from uuid import uuid4

from pydantic import constr
from pydantic import validator
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from say.authorization import get_user_role
from say.config import configs
from say.roles import *
from say.schema.base import CamelModel
from say.validations import ALLOWED_RECEIPT_EXTENSIONS
from say.validations import allowed_receipt


class UpdateReceiptSchema(CamelModel):
    attachment: Optional[Any]
    description: Optional[constr(max_length=1024)]
    title: Optional[constr(max_length=128)]
    is_public: Optional[bool]

    @validator('attachment')
    def attachment_validator(cls, v):
        if not isinstance(v, FileStorage):
            raise ValueError('attachment must be file')

        if not allowed_receipt(v.filename):
            raise ValueError(f'attachment must be {ALLOWED_RECEIPT_EXTENSIONS}')

        receipt_path = os.path.join(
            configs.UPLOAD_FOLDER,
            'receipts',
        )

        os.makedirs(receipt_path, exist_ok=True)

        v.filename = secure_filename(str(v.filename))
        v.filepath = f'{receipt_path}/{uuid4().hex}-{v.filename}'

        return v

    @validator('is_public')
    def is_public_validator(cls, v):
        role = get_user_role()

        if role not in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN] and v is True:
            raise ValueError(f'can not create public receipt with role {role}')

        return v


class NewReceiptSchema(UpdateReceiptSchema):

    attachment: Any
    code: constr(max_length=64)
    description: constr(max_length=1024) = None
    title: constr(max_length=128) = None
    is_public: bool = False
    owner_id: int


class ReceiptSchema(NewReceiptSchema):

    id: int
    deleted: datetime = None

    class Config:
        exclude = 'owner_id'
        orm_mode = True

    @validator('attachment')
    def attachment_validator(cls, v):
        return urljoin(
            configs.BASE_URL,
            v,
        )

    @validator('is_public')
    def is_public_validator(cls, v):
        return v

    @validator('owner_id')
    def owner_id_validator(cls, v):
        role = get_user_role()
        if role not in [SUPER_ADMIN, SAY_SUPERVISOR, ADMIN] and v is True:
            return None
        return v
