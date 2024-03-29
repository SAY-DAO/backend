import json

import requests


# DOCS: https://idpay.ir/web-service/v1.1/index.html


class IDPay:

    API_URL = "https://api.idpay.ir/v1.1/payment"
    TRY_COUNT = 3
    TIMEOUT = 59

    RESPONSES = {
        1: "پرداخت انجام نشده است",
        2: "پرداخت ناموفق بوده است",
        3: "خطا رخ داده است",
        4: "بلوکه شده",
        5: "برگشت به پرداخت کننده",
        6: "برگشت خورده سیستمی",
        10: "در انتظار تایید پرداخت",
        100: "پرداخت تایید شده است",
        101: "پرداخت قبلا تایید شده است",
        200: "به دریافت کننده واریز شد",
    }

    ERRORS = {
        11: "کاربر مسدود شده است.",
        12: "API Key یافت نشد.",
        13: "درخواست شما از {ip} ارسال شده است. این IP با IP های ثبت شده در وب سرویس همخوانی ندارد.",
        14: "وب سرویس تایید نشده است.",
        21: "حساب بانکی متصل به وب سرویس تایید نشده است.",
        31: "کد تراکنش id نباید خالی باشد.",
        32: "شماره سفارش order_id نباید خالی باشد.",
        33: "مبلغ amount نباید خالی باشد.",
        34: "مبلغ amount باید بیشتر از {min-amount} ریال باشد.",
        35: "مبلغ amount باید کمتر از {max-amount} ریال باشد.",
        36: "مبلغ amount بیشتر از حد مجاز است.",
        37: "آدرس بازگشت callback نباید خالی باشد.",
        38: "درخواست شما از آدرس {domain} ارسال شده است. دامنه آدرس بازگشت callback با آدرس ثبت شده در وب سرویس همخوانی ندارد.",
        51: "تراکنش ایجاد نشد.",
        52: "استعلام نتیجه ای نداشت.",
        53: "تایید پرداخت امکان پذیر نیست.",
        54: "مدت زمان تایید پرداخت سپری شده است.",
    }

    def __init__(self, api_key, sandbox=False):
        self.headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        if sandbox:
            self.headers["X-SANDBOX"] = '1'

    def request(self, route, **kwargs):
        # Retry for 5xx response
        for i in range(self.TRY_COUNT):
            response = requests.post(
                f'{self.API_URL}{route}',
                data=json.dumps(kwargs),
                headers=self.headers,
                timeout=self.TIMEOUT,
            )
            if response.status_code < 500 and response.status_code != 405:
                break

        response.raise_for_status()  # To raise ex for non OK responses
        result = response.json()
        return result

    def new_transaction(
        self,
        order_id: str,
        amount: int,
        callback: str,
        name: str = None,
        phone: str = None,
        mail: str = None,
        desc: str = None,
        reseller: int = None,
    ):

        amount *= 10  # RIAL to TOMAN
        return self.request(
            '',
            order_id=order_id,
            amount=amount,
            callback=callback,
            name=name,
            phone=phone,
            mail=mail,
            desc=desc,
            reseller=reseller,
        )

    def verify(self, id, order_id):
        return self.request('/verify', id=id, order_id=order_id)

    def inquiry(self, id, order_id):
        return self.request('/inquiry', id=id, order_id=order_id)
