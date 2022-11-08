from tests.helper import BaseTestClass


STATES_URL = '/api/v2/states/%s'
LIST_STATES_URL = '/api/v2/countries/%s/states'


class TestStates(BaseTestClass):
    def mockup(self):
        for _ in range(10):
            self.country = self._create_country()
            for _ in range(3):
                self._create_state(country=self.country)
            self.session.add(self.country)
        self.session.commit()

    def test_list_country_states(self):
        res = self.client.get(LIST_STATES_URL % self.country.id)
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]['id'] is not None
        assert result[0]['name'] is not None
        assert result[0]['stateCode'] is not None

    def test_get_states(self):
        res = self.client.get(STATES_URL % self.country.states[0].id)
        self.assert_ok(res)
        result = res.json
        assert result['id'] is not None
        assert result['name'] is not None

        res = self.client.get(STATES_URL % -1)
        self.assert_code(res, 404)
