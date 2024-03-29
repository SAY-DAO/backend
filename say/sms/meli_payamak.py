import requests


class MeliPayamakException(Exception):
    pass


class MeliPayamak:

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
                    **kwargs,
                },
                headers=self.headers,
            )
            json_resp = resp.json()
            status = json_resp.get('RetStatus', -1)
            if status != 1:
                raise MeliPayamakException(f'Failed with status {status}')

            return json_resp

        except Exception as ex:
            print(ex)
            raise ex

    def send(self, to, text):
        return self.request('/SendSMS/SendSMS', to=to, text=text)
