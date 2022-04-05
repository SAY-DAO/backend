from .base import CamelModel


class StateSchema(CamelModel):
    id: int
    name: str
    state_code: str
    country_id: int
    country_code: str
    country_name: str
    latitude: str = None
    longitude: str = None
    iso2: str = None
    type: str = None
    fips_code: str = None
