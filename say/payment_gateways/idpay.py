from say.config import config
from say.payment import IDPay

idpay = IDPay(config['IDPAY_API_KEY'], config['SANDBOX'])