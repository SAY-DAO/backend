from tests.helper import BaseTestClass


CITIES_URL = '/api/v2/cities/%s'
LIST_CITIES_URL = '/api/v2/states/%s/cities'


class TestCities(BaseTestClass):
    def mockup(self):
        for _ in range(10):
            self.state = self._create_state()
            for _ in range(5):
                self._create_city(state=self.state)
            self.session.add(self.state)
        self.session.commit()

    def test_list_state_cities(self):
        res = self.client.get(LIST_CITIES_URL % self.state.id)
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 5
        assert result[0]['id'] is not None
        assert result[0]['name'] is not None
        assert result[0]['stateName'] is not None
        assert result[0]['countryName'] is not None

    def test_get_city(self):
        res = self.client.get(CITIES_URL % self.state.cities[0].id)
        self.assert_ok(res)
        result = res.json
        assert result['id'] is not None
        assert result['name'] is not None
        assert result['stateName'] is not None
        assert result['countryName'] is not None

        res = self.client.get(CITIES_URL % -1)
        self.assert_code(res, 404)
