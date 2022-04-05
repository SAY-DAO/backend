from .base import CamelModel


class CitySchema(CamelModel):
    id: int
    name: str
    state_id: int
    state_code: str
    state_name: str
    country_id: int
    country_code: str
    country_name: str
    latitude: str
    longitude: str
