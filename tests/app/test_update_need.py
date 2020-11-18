from tests.helper import BaseTestClass

UPDATE_NEED_URL = '/api/v2/need/update/needId=%s'


class TestUpdateNeed(BaseTestClass):
    def mockup(self):
        self.password = '123456'
        self.user = self.create_user(self.password)

    def test_update_need_not_privilege_user(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers)

        assert res.status_code == 403

    def test_update_need_wrong_need_id(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers)

        assert res.status_code == 404

    def test_update_need_change_cost_of_confirmed_need(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456  # TODO get a real need id
        new_cost = 4000
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers,
                                data={"cost": new_cost}
                                )

        assert res.status_code == 402

    def test_update_need_change_cost_of_not_confirmed_need(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456  # TODO get a real need id
        new_cost = 4000
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers,
                                data={"cost": new_cost}
                                )

        assert res.status_code == 402

    def test_update_need_change_purchase_cost_wrong_state(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456  # TODO get a real need id
        purchase_cost = 4000
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers,
                                data={"purchase_cost": purchase_cost}
                                )

        assert res.status_code == 402

    def test_update_need_change_purchase_cost(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456  # TODO get a real need id
        purchase_cost = 4000
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers,
                                data={"purchase_cost": purchase_cost}
                                )

        assert res.status_code == 402

    def test_update_need_change_status(self):
        token = self.login(self.user.userName, self.password)
        headers = {"Authorization": token}

        need_id = 23456  # TODO get a real need id
        status = 1
        res = self.client.patch(UPDATE_NEED_URL % need_id,
                                headers=headers,
                                data={"status": status}
                                )

        assert res.status_code == 402
