import requests
from say.config import configs
from urllib.parse import urljoin


class ZIBAL:
    merchant = configs.ZIBAL_MERCHANT_ID
    pay_callback_url = urljoin(configs.NEST_API_URL, "api/dao/payment/verify")
    cart_callback_url = urljoin(configs.NEST_API_URL, "api/dao/payment/verify")

    RESPONSES = {
        -1: " در انتظار پردخت",
        -2: "خطای داخلی",
        1: "پرداخت شده - تاییدشده",
        2: "پرداخت شده - تاییدنشده",
        3: "لغوشده توسط کاربر",
        4: "‌شماره کارت نامعتبر می‌باشد.",
        5: "‌موجودی حساب کافی نمی‌باشد.",
        6: "رمز واردشده اشتباه می‌باشد.",
        7: "‌تعداد درخواست‌ها بیش از حد مجاز می‌باشد.",
        8: "‌تعداد پرداخت اینترنتی روزانه بیش از حد مجاز می‌باشد.",
        9: "مبلغ پرداخت اینترنتی روزانه بیش از حد مجاز می‌باشد.",
        10: "‌صادرکننده‌ی کارت نامعتبر می‌باشد.",
        11: "‌خطای سوییچ",
        12: "کارت قابل دسترسی نمی‌باشد.",
    }

    ERRORS = {
        100: "کاربر مسدود شده است.",
        102: "merchant یافت نشد.",
        103: "merchant غیرفعال",
        104: "merchant نامعتبر",
        105: "amount بایستی بزرگتر از 1,000 ریال باشد.",
        106: "callbackUrl نامعتبر می‌باشد. (شروع با http و یا https)",
        113: "amount مبلغ تراکنش از سقف میزان تراکنش بیشتر است.",
    }

    def request(self, is_cart, amount, order_id, description, multiplexingInfos=None):
        data = {}
        data["merchant"] = self.merchant
        if is_cart == False:
            data["callbackUrl"] = self.pay_callback_url
        if is_cart == True:
            data["callbackUrl"] = self.cart_callback_url
        data["amount"] = amount * 10  # RIAL to TOMAN
        data["orderId"] = order_id
        data["description"] = description
        data["multiplexingInfos"] = multiplexingInfos

        if self.merchant == "zibal":
            return {"response": "Zibal test account!"}, 400

        response = self.postTo("request", data)
        return response

    def verify(self, trackId):
        data = {}
        data["merchant"] = self.merchant
        data["trackId"] = trackId
        return self.postTo("verify", data)

    def postTo(self, path, parameters):
        url = "https://gateway.zibal.ir/v1/" + path

        response = requests.post(url=url, json=parameters)

        return response.json()
