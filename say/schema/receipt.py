import os
from datetime import datetime
from typing import Any
from urllib.parse import urljoin
from uuid import uuid4

from pydantic import constr, validator

from say.config import configs
from say.models.receipt import Receipt
from say.schema.base import CamelModel
from say.validations import ALLOWED_RECEIPT_EXTENSIONS, allowed_receipt
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename


class NewReceiptSchema(CamelModel):

    attachment: Any
    code: constr(max_length=64)
    description: constr(max_length=1024) = ''
    title: constr(max_length=128) = ''
    is_public: bool = False
    owner_id: int

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


class ReceiptSchema(NewReceiptSchema):

    id: int
    deleted: datetime = None

    class Config:
        exclude = 'owner_id'
        orm_mode=True 
    
    @validator('attachment')
    def attachment_exporter(cls, v):
        return urljoin(
            configs.BASE_URL,
            v,
        )
