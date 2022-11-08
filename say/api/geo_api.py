from flasgger import swag_from
from flask_restful import Resource

from say.api.ext import api
from say.api.ext import cache
from say.decorators import json
from say.exceptions import HTTP_NOT_FOUND
from say.models import City
from say.models import Country
from say.models import State
from say.orm import session
from say.schema.city import CitySchema
from say.schema.country import CountrySchema
from say.schema.state import StateSchema


class CountriesAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json(CountrySchema, use_list=True)
    @swag_from('./docs/geo/countries.yml')
    def get(self):
        return session.query(Country)


class StateCitiesAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json(CitySchema, use_list=True)
    @swag_from('./docs/geo/cities.yml')
    def get(self, id):
        return session.query(City).filter(City.state_id == id)


class CountryStatesAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json(StateSchema, use_list=True)
    @swag_from('./docs/geo/states.yml')
    def get(self, id):
        return session.query(State).filter(State.country_id == id)


class CityAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json(CitySchema)
    @swag_from('./docs/geo/get-city.yml')
    def get(self, id):
        city = session.query(City).get(id)
        if city is None:
            raise HTTP_NOT_FOUND()

        return city


class StateAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json(StateSchema)
    @swag_from('./docs/geo/get-state.yml')
    def get(self, id):
        state = session.query(State).get(id)
        if state is None:
            raise HTTP_NOT_FOUND()

        return state


class CountryAPI(Resource):
    @cache.cached(timeout=10 * 60)
    @json(CountrySchema)
    @swag_from('./docs/geo/get-country.yml')
    def get(self, id):
        country = session.query(Country).get(id)
        if country is None:
            raise HTTP_NOT_FOUND()

        return country


api.add_resource(
    CityAPI,
    '/api/v2/cities/<int:id>',
)

api.add_resource(
    StateAPI,
    '/api/v2/states/<int:id>',
)

api.add_resource(
    CountryAPI,
    '/api/v2/countries/<int:id>',
)

api.add_resource(
    CountriesAPI,
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
