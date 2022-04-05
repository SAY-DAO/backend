from .base import CamelModel


class CountrySchema(CamelModel):
    id: int
    name: str
    iso2: str = None
    iso3: str = None
    numeric_code: str = None
    phone_code: str = None
    capital: str = None
    currency: str = None
    currency_name: str = None
    currency_symbol: str = None
    tld: str = None
    native: str = None
    region: str = None
    subregion: str = None
    timezones: str = None
    translations: str = None
    latitude: str = None
    longitude: str = None
    emoji: str = None
    emojiU: str = None
