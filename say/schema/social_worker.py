from datetime import date
from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field
from pydantic import conint
from pydantic.networks import EmailStr
from pydantic.types import constr

from say.config import configs
from say.constants import MB
from say.schema.base import AllOptionalMeta
from say.schema.base import CamelModel
from say.schema.city import CitySchema
from say.schema.need_status_update import NeedStatusUpdateSchema
from say.schema.participant import ParticipantSchema
from say.schema.payment import PaymentSchema
from say.schema.receipt import ReceiptSchema
from say.schema.types import Locale
from say.schema.types import Password
from say.schema.types import PhoneNumber
from say.schema.types import confilestorage
from say.schema.types.password import conpassword
from say.validations import ALLOWED_IMAGE_EXTENSIONS


class MigrateSocialWorkerChildrenSchema(CamelModel):
    destination_social_worker_id: int


class NewSocialWorkerSchema(CamelModel):
    city_id: Optional[int]
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
    current_password: Optional[Password]


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
    city: Optional[CitySchema]


class NeedSchema(CamelModel):
    id: int
    created_by_id: int = None
    name: str
    title: str = None
    status: int
    imageUrl: str = Field(alias='imageUrl')
    category: int
    type: int
    isUrgent: bool = Field(alias='isUrgent')
    link: str = None
    affiliateLinkUrl: str = Field(None, alias='affiliateLinkUrl')
    doing_duration: int
    img: str = None
    paid: int
    purchase_cost: int = None
    cost: int
    unpayable: bool
    isDone: bool = Field(alias='isDone')
    doneAt: datetime = Field(None, alias='doneAt')
    isConfirmed: bool = Field(alias='isConfirmed')
    unpayable_from: datetime = None
    created: datetime
    updated: datetime
    confirmDate: datetime = Field(None, alias='confirmDate')
    confirmUser: int = Field(None, alias='confirmedBy')
    status_updates: List[NeedStatusUpdateSchema]
    receipts_: List[ReceiptSchema] = Field(alias='receipts_')
    verified_payments: List[PaymentSchema]
    ngo_delivery_date: datetime = None
    child_delivery_date: datetime = None
    purchase_date: datetime = None
    bank_track_id: str = None
    expected_delivery_date: datetime = None


class SocialWorkerMyPageSchema(CamelModel):
    id: int
    sayName: str = Field(alias='sayName')
    firstName: str = Field(alias='firstName')
    lastName: str = Field(alias='lastName')
    birthDate: date = Field(alias='birthDate')
    awakeAvatarUrl: str = Field(alias='awakeAvatarUrl')
    needs: List[NeedSchema]


class MyPagePaginationSchema(CamelModel):
    take: conint(ge=1, le=50) = Field(
        10,
        alias=configs.PAGINATION_TAKE_HEADER_KEY,
    )

    skip: conint(ge=0, le=configs.POSTRGES_MAX_BIG_INT) = Field(
        0,
        alias=configs.PAGINATION_SKIP_HEADER_KEY,
    )

    class Config:
        extra = 'ignore'


class MyPageQuerySchema(CamelModel):
    sw_id: Optional[int]


class ChangePassword(CamelModel):
    new_password: conpassword(
        min_length=8,
        includes_lowercase=True,
        includes_special_chars=True,
        includes_numbers=True,
        includes_uppercase=True,
    )
    current_password: str
