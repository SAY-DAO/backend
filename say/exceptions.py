from dataclasses import dataclass
from functools import partial


@dataclass
class HTTPException(Exception):
    status_code: int
    message: str

    def to_dict(self):
        return self.__dict__


HTTP_PERMISION_DENIED = partial(
    HTTPException, message='Permission Denied', status_code=403
)
HTTP_NOT_FOUND = partial(HTTPException, message='Not Found', status_code=404)
HTTP_UNAUTHORIZED = partial(HTTPException, message='Unauthorized', status_code=401)


class InvalidLocale(Exception):
    pass


class PaidUnverifiedPaymentError(Exception):
    """Raise when a paid unverified payment found"""


class AmountTooLow(ValueError):
    pass


class AmountTooHigh(ValueError):
    pass
