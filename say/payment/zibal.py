import requests
from ..config import configs


class ZIBAL:
    merchant = configs.ZIBAL_MERCHANT_ID
    callback_url = "https://api.sayapp.company/api/payments/verify"

    ERRORS = {
        100: "کاربر مسدود شده است.",
        102: "merchant یافت نشد.",
        103: "merchant غیرفعال",
        104: "merchant نامعتبر",
        105: "amount بایستی بزرگتر از 1,000 ریال باشد.",
        106: "callbackUrl نامعتبر می‌باشد. (شروع با http و یا https)",
        113: "amount مبلغ تراکنش از سقف میزان تراکنش بیشتر است.",
    }

    def request(self, amount, order_id, description, multiplexingInfos=None):
        data = {}
        data["merchant"] = self.merchant
        data["callbackUrl"] = self.callback_url
        data["amount"] = amount
        data["orderId"] = order_id
        data["description"] = description
        data["multiplexingInfos"] = multiplexingInfos

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