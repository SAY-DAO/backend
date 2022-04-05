from tests.helper import BaseTestClass


LIST_COUNTRIES_URL = '/api/v2/countries'


class TestListCountries(BaseTestClass):
    def mockup(self):
        for _ in range(10):
            c = self._create_country()
            for _ in range(5):
                self._create_city(country=c)
            self.session.add(c)
        self.session.commit()

    def test_list_countries(self):
        res = self.client.get(LIST_COUNTRIES_URL)
        self.assert_ok(res)
        result = res.json
        assert isinstance(result, list)
        assert len(result) == 10
        assert result[0]['id'] is not None
        assert result[0]['name'] is not None
