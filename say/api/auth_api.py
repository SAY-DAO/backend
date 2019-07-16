from pyotp import TOTP, random_base32

from . import *

"""
Authentication APIs
"""


class Register(Resource):
    def post(self): pass
        # session_maker = sessionmaker(db)
        # session = session_maker()
        #
        # PhoneNumber = request.form['PhoneNumber']
        # DeviceInfo = request.form['DeviceInfo']
        # CountryCode = request.form['CountryCode']
        # OtpCode = request.form['OtpCode']





class Login(Resource):
    def post(self): pass


class SendOtp(Resource):
    def post(self): pass
        # random_otp = TOTP(random_base32())
        # otp_code = random_otp.now()


class ResendOtp(Resource):
    def post(self): pass


"""
API URLs
"""

api.add_resource(Register, '/api/v2/auth/register')
api.add_resource(Login, '/api/v2/auth/login')
api.add_resource(SendOtp, '/api/v2/auth/sendOtp')
api.add_resource(ResendOtp, '/api/v2/auth/resendOtp')
