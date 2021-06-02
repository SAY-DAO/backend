from datetime import datetime

from say.config import configs
from say.models import Payment
from say.orm import create_engine
from say.orm import init_model
from say.orm import session
from say.payment import IDPay


def check_unverified_payments():
    # db
    engine = session.bind or create_engine(url=configs.postgres_url)
    init_model(engine)

    # idpay (Payment Gateway)
    idpay = IDPay(configs.IDPAY_API_KEY, configs.SANDBOX)

    unverified_payment = session.query(Payment).filter(
        Payment.link.isnot(None),
        Payment.verified.is_(None),
    )
    count = unverified_payment.count()
    for i, p in enumerate(unverified_payment):
        print(f'{round(i / count * 100)}%, {i+1}/{count}')
        try:
            res = idpay.inquiry(p.gateway_payment_id, p.order_id)
            if res.get('status') in (100, 101, 200):
                print('!!! PAYMENT IS VERIFIED !!!')
                print('Payment ID: ', p.id)
                print('Payment Gateway ID: ', p.gateway_payment_id)
                print('Payment Order ID: ', p.order_id)
                print('Need ID: ', p.id_need)
                print('User ID: ', p.id_user)
                print('Need Amount: ', p.need_amount)
                print('Bank Amount: ', p.bank_amount)
                print(
                    'Payment Verified AT:',
                    res['verify']['date'],
                    datetime.fromtimestamp(res['verify']['date']),
                )

        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    check_unverified_payments()
