# from datetime import datetime

# from say.roles import ADMIN
# from say.roles import NGO_SUPERVISOR
# from say.roles import SAY_SUPERVISOR
# from say.roles import SOCIAL_WORKER
# from say.roles import SUPER_ADMIN
# from tests.helper import BaseTestClass


# LIST_NEEDS_URL = '/api/v2/needs'
# RECEIPT_URL = '/api/v2/receipts/'


# class TestNeedReceipts(BaseTestClass):
#     def mockup(self):
#         self.sw = self.create_panel_user()

#         self.need = self._create_random_need()
#         self.r1 = self._create_need_receipt(
#             need=self.need,
#             receipt=self._create_random_receipt(is_public=False),
#         )

#         self.public_receipt = self._create_need_receipt(
#             need=self.need,
#             receipt=self._create_random_receipt(is_public=True),
#         )

#         self.deleted_receipt = self._create_need_receipt(
#             need=self.need,
#             deleted=datetime.utcnow(),
#         )

#     def test_receipts_count(self):
#         self.login_sw(self.sw)

#         res = self.client.get(LIST_NEEDS_URL)
#         self.assert_ok(res)
#         needs = res.json['needs']
#         assert needs[0]['receipt_count'] == 2

#     def test_get_public_receipt(self):
#         res = self.client.get(RECEIPT_URL + str(self.public_receipt.id))
#         self.assert_ok(res)
#         assert res.json['ownerId'] is None

#         self.login_as_user()
#         res = self.client.get(RECEIPT_URL + str(self.public_receipt.id))
#         self.assert_ok(res)
#         assert res.json['ownerId'] is None

#         for role in [SAY_SUPERVISOR, ADMIN, SUPER_ADMIN]:
#             self.login_as_sw(role)
#             res = self.client.get(RECEIPT_URL + str(self.public_receipt.id))
#             self.assert_ok(res)
#             assert res.json['ownerId'] is not None

#         self.login_as_sw(SOCIAL_WORKER)
#         res = self.client.get(
#             RECEIPT_URL + str(self.public_receipt.id),
#         )
#         self.assert_ok(res)

#     def test_get_private_receipt(self):
#         res = self.client.get(RECEIPT_URL + str(self.r1.id))
#         assert res.status_code == 404

#         self.login_as_sw(SUPER_ADMIN)
#         res = self.client.get(RECEIPT_URL + str(self.r1.id))
#         self.assert_ok(res)
#         assert res.json['id'] == self.r1.id

#         res = self.client.get(RECEIPT_URL + str(self.deleted_receipt))
#         assert res.status_code == 404

#         self.login_sw(self.r1.owner)
#         res = self.client.get(RECEIPT_URL + str(self.r1.id))
#         self.assert_ok(res)

#         self.login_as_sw(SOCIAL_WORKER)
#         res = self.client.get(RECEIPT_URL + str(self.r1.id))
#         assert res.status_code == 404

#         ngo_super_visor = self._create_random_sw(
#             role=NGO_SUPERVISOR,
#             ngo=self.need.child.ngo,
#         )
#         self.login_sw(ngo_super_visor)
#         res = self.client.get(RECEIPT_URL + str(self.r1.id))
#         self.assert_ok(res)
