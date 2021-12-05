import os
from typing import Any
from typing import Dict
from typing import Optional
from typing import Set
from typing import Type

from pydantic.errors import PydanticTypeError
from pydantic.errors import PydanticValueError
from pydantic.types import OptionalInt
from pydantic.utils import update_not_none
from werkzeug.datastructures import FileStorage


class FileTypeError(PydanticTypeError):
    msg_template = 'value is not a valid file'


class FileTooLargeError(PydanticValueError):
    msg_template = 'file is too large'


class FileExtensionError(PydanticTypeError):
    msg_template = 'file extension is not valid'


class ConstrainedFileStorage(FileStorage):
    """Constrained file validator for flask's FileStorage"""

    max_size: OptionalInt = None  # bytes
    valid_extensions: Optional[Set[str]] = None

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        update_not_none(
            field_schema,
            maxSize=cls.max_size,
            valid_extensions=cls.valid_extensions,
        )

    @classmethod
    def __get_validators__(cls):
        yield cls.strict_file_storage_validator
        yield cls.validate_size
        yield cls.validate_extension

    @classmethod
    def strict_file_storage_validator(cls, v: Any) -> FileStorage:
        if not isinstance(v, FileStorage):
            raise FileTypeError()

        return v

    @classmethod
    def validate_size(cls, v: FileStorage):
        v.stream.seek(0, os.SEEK_END)  # seek to end
        file_size = v.stream.tell()
        if cls.max_size and file_size > cls.max_size:
            raise FileTooLargeError()

        v.stream.seek(0, os.SEEK_SET)  # seek back to start
        return v

    @classmethod
    def validate_extension(cls, v: FileStorage):
        _, extension = os.path.splitext(v.filename)
        if cls.valid_extensions and extension.strip('.') not in cls.valid_extensions:
            raise FileExtensionError()

        return v


def confilestorage(
    *,
    max_size: int = None,
    valid_extensions: Set[str] = None,
) -> Type[FileStorage]:
    # use kwargs then define conf in a dict to aid with IDE type hinting
    namespace = dict(
        max_size=max_size,
        valid_extensions=valid_extensions,
    )
    return type('ConstrainedFileStorage', (ConstrainedFileStorage,), namespace)
