from typing import Set
from typing import Type

from pydantic import SecretStr


class Password(SecretStr):
    """Pydantic type for password"""

    SPECIAL_CHARS = [
        '$',
        '@',
        '#',
        '%',
        '!',
        '^',
        '&',
        '*',
        '(',
        ')',
        '-',
        '_',
        '+',
        '=',
        '{',
        '}',
        '[',
        ']',
    ]

    MIN_LENGTH = 8
    INCLUDES_SPECIAL_CHARS = False
    INCLUDES_NUMBERS = False
    INCLUDES_LOWERCASE = False
    INCLUDES_UPPERCASE = False

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')

        if len(v) < cls.MIN_LENGTH:
            raise ValueError(f'length should be at least {cls.MIN_LENGTH}')

        if cls.INCLUDES_NUMBERS and not any(char.isdigit() for char in v):
            raise ValueError('Password should have at least one numeral')

        if cls.INCLUDES_UPPERCASE and not any(char.isupper() for char in v):
            raise ValueError('Password should have at least one uppercase letter')

        if cls.INCLUDES_LOWERCASE and not any(char.islower() for char in v):
            raise ValueError('Password should have at least one lowercase letter')

        if cls.INCLUDES_SPECIAL_CHARS and not any(
            char in cls.SPECIAL_CHARS for char in v
        ):
            raise ValueError(
                f'Password should have at least one of the symbols {cls.SPECIAL_CHARS}'
            )

        return cls(v)


def conpassword(
    *,
    min_length: int = 8,
    includes_special_chars: bool = False,
    special_chars: Set[str] = Password.SPECIAL_CHARS,
    includes_numbers: bool = False,
    includes_lowercase: bool = False,
    includes_uppercase: bool = False,
) -> Type[Password]:
    # use kwargs then define conf in a dict to aid with IDE type hinting
    namespace = dict(
        SPECIAL_CHARS=special_chars,
        MIN_LENGTH=min_length,
        INCLUDES_SPECIAL_CHARS=includes_special_chars,
        INCLUDES_NUMBERS=includes_numbers,
        INCLUDES_LOWERCASE=includes_lowercase,
        INCLUDES_UPPERCASE=includes_uppercase,
    )
    return type('ConstrainedPassword', (Password,), namespace)
