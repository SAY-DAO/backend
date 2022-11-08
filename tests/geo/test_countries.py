from tests.helper import BaseTestClass


LIST_COUNTRIES_URL = '/api/v2/countries'
COUNTRIES_URL = LIST_COUNTRIES_URL + '/%s'


class TestListCountries(BaseTestClass):
    def mockup(self):
        for _ in range(10):
            self.c = self._create_country()
            for _ in range(5):
                self._create_city(country=self.c)
            self.session.add(self.c)
        self.session.commit()

    def test_list_countries(self):
        res = self.client.get(LIST_COUNTRIES_URL)
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 10
        assert result[0]['id'] is not None
        assert result[0]['name'] is not None
        assert result[0]['currencyName'] is not None

    def test_get_country(self):
        res = self.client.get(COUNTRIES_URL % self.c.id)
        self.assert_ok(res)
        result = res.json
        assert result['id'] is not None
        assert result['name'] is not None

        res = self.client.get(COUNTRIES_URL % -1)
        self.assert_code(res, 404)
