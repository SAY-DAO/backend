import requests
import json


class MelliPayamak:

    API_URL = 'https://rest.payamak-panel.com/api'

    def __init__(self, username, password, from_):
        self.username = username
        self.password = password
        self.from_ = from_
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'cache-control': 'no-cache',
        }

    def request(self, route, **kwargs):
        try:
            resp = requests.post(
                f'{self.API_URL}{route}',
                data={
                    'username': self.username,
                    'password': self.password,
                    'from': self.from_,
                    **kwargs
                },
                headers=self.headers,
            )
            import pudb; pudb.set_trace()  # XXX BREAKPOINT
            return resp.json()

        except Exception as ex:
            print(ex)
            raise ex

    def send(self, to, text):
        return self.request('/SendSMS/SendSMS', to=to, text=text)

m = MelliPayamak('9123186846', r'%4o8t&F9in+', '10007778777827')
a = m.send('989372735711', 'hey you')
