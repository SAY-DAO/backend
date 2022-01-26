import babel


class Locale(babel.Locale, str):
    """Pydantic Locale type"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> babel.Locale:
        try:
            return babel.Locale.parse(v)
        except (ValueError, babel.core.UnknownLocaleError):
            raise ValueError('invalid locale')
