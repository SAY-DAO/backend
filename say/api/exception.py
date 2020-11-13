from dataclasses import dataclass


@dataclass
class HTTPException(Exception):
    status_code: int
    message: str

    def to_dict(self):
        return self.__dict__
