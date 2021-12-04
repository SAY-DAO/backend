from datetime import date
from typing import Optional

from pydantic.networks import EmailStr
from pydantic.types import constr

from say.constants import MB
from say.schema.base import BaseModel
from say.schema.base import CamelModel
from say.schema.types import PhoneNumber
from say.schema.types import confilestorage
from say.validations import ALLOWED_DOCUMENT_EXTENSIONS
from say.validations import ALLOWED_IMAGE_EXTENSIONS


class MigrateSocialWorkerChildrenSchema(CamelModel):
    destination_social_worker_id: int


class NewSocialWorkerSchema(BaseModel):
    country: Optional[int]
    city: Optional[int]
    firstName: Optional[constr(max_length=64, strip_whitespace=True)]
    lastName: constr(max_length=64, strip_whitespace=True)
    birthCertificateNumber: constr(max_length=32, strip_whitespace=True)
    passportNumber: Optional[constr(max_length=32, strip_whitespace=True)]
    postalAddress: Optional[constr(max_length=256, strip_whitespace=True)]
    bankAccountNumber: Optional[constr(max_length=64, strip_whitespace=True)]
    bankAccountShebaNumber: Optional[constr(max_length=64, strip_whitespace=True)]
    bankAccountCardNumber: Optional[constr(max_length=64, strip_whitespace=True)]
    birthDate: Optional[date]
    telegramId: constr(max_length=64, strip_whitespace=True)
    idNumber: constr(max_length=64, strip_whitespace=True)
    id_ngo: int
    id_type: int
    gender: bool
    phoneNumber: PhoneNumber
    emergencyPhoneNumber: PhoneNumber
    emailAddress: EmailStr
    avatarUrl: confilestorage(
        max_size=4 * MB,
        valid_extensions=ALLOWED_IMAGE_EXTENSIONS,
    )

    idCardUrl: Optional[
        confilestorage(
            max_size=4 * MB,
            valid_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
        )
    ]

    passportUrl: Optional[
        confilestorage(
            max_size=4 * MB,
            valid_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
        )
    ]
