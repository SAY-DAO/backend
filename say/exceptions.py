from dataclasses import dataclass
from functools import partial


@dataclass
class HTTPException(Exception):
    status_code: int
    message: str

    def to_dict(self):
        return self.__dict__


HTTP_PERMISION_DENIED = partial(HTTPException, message='Permission Denied', status_code=403)
HTTP_NOT_FOUND = partial(HTTPException, message='Not Found', status_code=404)


class InvalidLocale(Exception):
    pass
