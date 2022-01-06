from datetime import date
from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field
from pydantic.networks import EmailStr
from pydantic.types import constr

from say.constants import MB
from say.schema.base import AllOptionalMeta
from say.schema.base import BaseModel
from say.schema.base import CamelModel
from say.schema.types import Locale
from say.schema.types import Password
from say.schema.types import PhoneNumber
from say.schema.types import confilestorage
from say.validations import ALLOWED_IMAGE_EXTENSIONS


class MigrateSocialWorkerChildrenSchema(CamelModel):
    destination_social_worker_id: int


class NewSocialWorkerSchema(CamelModel):
    country: Optional[int]
    city: Optional[int]
    first_name: Optional[constr(max_length=64, strip_whitespace=True)]
    last_name: constr(max_length=64, strip_whitespace=True)
    birth_certificate_number: Optional[constr(max_length=32, strip_whitespace=True)]
    passport_number: Optional[constr(max_length=32, strip_whitespace=True)]
    postal_address: Optional[constr(max_length=256, strip_whitespace=True)]
    bank_account_number: Optional[constr(max_length=64, strip_whitespace=True)]
    bank_account_sheba_number: Optional[constr(max_length=64, strip_whitespace=True)]
    bank_account_card_number: Optional[constr(max_length=64, strip_whitespace=True)]
    birth_date: Optional[date]
    telegram_id: constr(max_length=64, strip_whitespace=True)
    id_number: constr(max_length=64, strip_whitespace=True)
    is_coordinator: Optional[bool]
    ngo_id: int
    type_id: int
    gender: bool
    phone_number: PhoneNumber
    emergency_phone_number: PhoneNumber
    email: EmailStr
    avatar_url: confilestorage(
        max_size=4 * MB,
        valid_extensions=ALLOWED_IMAGE_EXTENSIONS,
    )

    id_card_url: Optional[
        confilestorage(
            max_size=4 * MB,
            valid_extensions=ALLOWED_IMAGE_EXTENSIONS,
        )
    ]

    passport_url: Optional[
        confilestorage(
            max_size=4 * MB,
            valid_extensions=ALLOWED_IMAGE_EXTENSIONS,
        )
    ]


class UpdateSocialWorkerSchema(NewSocialWorkerSchema, metaclass=AllOptionalMeta):
    username: Optional[constr(strip_whitespace=True, min_length=3)]  # TODO: add validator
    password: Optional[Password]


class SocialWorkerSchema(NewSocialWorkerSchema):
    id: int
    avatar_url: str
    id_card_url: Optional[str]
    passport_url: Optional[str]
    username: str
    generated_code: str
    child_count: int
    current_child_count: int
    created: datetime
    updated: datetime
    need_count: int
    current_need_count: int
    last_login_date: datetime
    is_active: bool
    is_deleted: bool
    locale: Locale
    type_name: str
    ngo_name: str
