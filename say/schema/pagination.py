from pydantic import Field
from pydantic import conint

from say.config import configs
from say.schema.base import BaseModel


class PaginationSchema(BaseModel):
    take: conint(ge=1, le=configs.PAGINATION_MAX_TAKE) = Field(
        configs.PAGINATION_DEFAULT_TAKE,
        alias=configs.PAGINATION_TAKE_HEADER_KEY,
    )

    skip: conint(ge=0, le=configs.POSTRGES_MAX_BIG_INT) = Field(
        0,
        alias=configs.PAGINATION_SKIP_HEADER_KEY,
    )

    class Config:
        extra = 'ignore'
