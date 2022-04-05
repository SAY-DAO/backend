from flasgger import swag_from
from flask_restful import Resource

from say.api.ext import api
from say.api.ext import cache
from say.decorators import json
from say.models import City
from say.models import Country
from say.models import State
from say.orm import session


class CountryAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json
    @swag_from('./docs/geo/countries.yml')
    def get(self):
        return session.query(Country)


class StateCitiesAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json
    @swag_from('./docs/geo/cities.yml')
    def get(self, id):
        return session.query(City).filter(City.state_id == id)


class CountryStatesAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json
    @swag_from('./docs/geo/states.yml')
    def get(self, id):
        return session.query(State).filter(State.country_id == id)


api.add_resource(
    CountryAPI,
    '/api/v2/countries',
)
api.add_resource(
    CountryStatesAPI,
    '/api/v2/countries/<int:id>/states',
)
api.add_resource(
    StateCitiesAPI,
    '/api/v2/states/<int:id>/cities',
)
