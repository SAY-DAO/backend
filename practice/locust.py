from random import randint

from locust.contrib.fasthttp import FastHttpUser

from locust import between, task, SequentialTaskSet


class PerformanceTest(FastHttpUser):
    wait_time = between(0, .1)

    user_id = None

    # @task
    def on_start(self):
        login_resp = self.client.post(
            '/api/v2/auth/login?_lang=fa',
            data={'username': 'rhonin', 'password': 2, 'isInstalled': 1},
        ).json()

        self.token = login_resp['accessToken']

    @task
    def dashboard(self):
        self.client.get(
            '/api/v2/dashboard',
            headers={
                'Authorization': self.token,
            },
        )

    # @task
    # def add_missing(self):
    #     t = '1010-07-14T17:42:53'
    #     self.client.post(
    #         f'/time/add?t={t}',
    #         json=dict(
    #             hours=randint(1, 24),
    #         ),
    #         headers={
    #             'X-IDENTITY': self.token,
    #         },
    #     )

    # @task
    # def get(self):
    #     self.client.get(
    #         f'/time/get?from=2020-01-01T00:00:00&to=2021-01-01T00:00:00',
    #         headers={
    #             'X-IDENTITY': self.token,
    #         },
    #     )

    # @task
    # def get_sum(self):
    #     self.client.get(
    #         f'/time/calculator?from=2020-01-01T00:00:00&to=2021-01-01T00:00:00',
    #         headers={
    #             'X-IDENTITY': self.token,
    #         },
    #     )
