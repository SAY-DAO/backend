import logging
from logging import ERROR
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .config import configs


def traces_sampler(sampling_context):
    op = sampling_context['transaction_context']['op']
    if op == 'celery.task':
        task = sampling_context['celery_job']['task']
        if task == 'say.tasks.update_needs.update_need':
            return 0.05
        else:
            return 1
    elif op == 'http.server':
        path = sampling_context['wsgi_environ']['PATH_INFO']
        if path == '/api/healthz':
            return 0.1
        else:
            return 0.7
    else:
        return 0.5


def setup_sentry():
    # Monkypatching max string sent to sentry to get the full db transactions
    from sentry_sdk import utils
    utils.MAX_STRING_LENGTH = 4000

    sentry_sdk.init(
        dsn=configs.SENTRY_DSN,
        environment=configs.ENVIRONMENT,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        # traces_sample_rate=configs.SENTRY_SAMPLE_RATE,
        traces_sampler=traces_sampler,
        _experiments={"auto_enabling_integrations": True},
    )
