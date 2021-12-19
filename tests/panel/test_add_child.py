# from random import randint

# from say.models import Child
# from say.roles import SUPER_ADMIN
# from tests.helper import BaseTestClass


# ADD_CHILD_URL = '/api/v2/child/add/t'


# class TestAddChild(BaseTestClass):
#     def test_add_child(self):
#         admin = self.login_as_sw(role=SUPER_ADMIN)

#         data = dict(
#             firstName='asd',
#             ngo_id=admin.id_ngo,
#             sw_id=admin.id,
#             id_type=1,
#             lastName='qw',
#             telegramId=123456789,
#             idNumber='12345666',
#             gender='true',
#             birthCertificateNumber='1234567890',
#             phoneNumber=f'+98{randint(10000, 1000000)}',
#             emergencyPhoneNumber=f'+98{randint(10000, 1000000)}',
#             emailAddress=f'{randint(10000, 1000000)}@test.com',
#             avatarUrl=self.create_test_file('imageUrl.jpg', size=10000),
#         )

#         res = self.client.post(
#             ADD_CHILD_URL,
#             content_type='multipart/form-data',
#             data=data,
#         )

#         self.assert_ok(res)
#         assert res.json['id'] is not None
