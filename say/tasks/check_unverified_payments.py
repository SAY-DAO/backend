from datetime import datetime
from datetime import timedelta

import requests

from say.celery import celery
from say.config import configs
from say.exceptions import PaidUnverifiedPaymentError


@celery.task(base=celery.DBTask, bind=True, max_retries=5, queue='slow')
def check_unverified_payment(self, id):
    from say.models import Payment
    from say.payment import IDPay

    # idpay (Payment Gateway)
    idpay = IDPay(configs.IDPAY_API_KEY, configs.SANDBOX)

    p = self.session.query(Payment).get(id)
    try:
        res = idpay.inquiry(p.gateway_payment_id, p.order_id)
        if res.get('status') in (100, 101, 200):
            raise PaidUnverifiedPaymentError(f'Payment ID: {id}')
    except requests.exceptions.HTTPError:
        pass
    except requests.exceptions.RequestException:
        raise
    return


@celery.task(base=celery.DBTask, bind=True)
def check_unverified_payments(self):
    from say.models import Payment

    unverified_payments = self.session.query(Payment.id).filter(
        Payment.link.isnot(None),
        Payment.verified.is_(None),
        datetime.utcnow() - Payment.created <= timedelta(hours=25),
    )

    t = []
    for p_id in unverified_payments:
        t.append(p_id)
        check_unverified_payment.delay(p_id)

    return t
