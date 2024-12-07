from celery import Celery
from celery.schedules import crontab
from kombu import Exchange
from kombu import Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from say.config import configs
from say.orm import init_model
from say.sentry import setup_sentry


CELERY_TASK_LIST = [
    'say.tasks',
]


beat = {
    'report-to-social-workers': {
        'task': 'say.tasks.report_to_social_worker.report_to_social_workers',
        'schedule': crontab(minute=30, hour='2,9'),
    },
    'update-needs': {
        'task': 'say.tasks.update_needs.update_needs',
        'schedule': crontab(minute=30, hour='6,12,16,20'),
    },
    'report_to_family': {
        'task': 'say.tasks.report_to_family.report_to_families',
        'schedule': crontab(minute=30, hour='4'),
    },
    'report_unpayables': {
        'task': 'say.tasks.report_unpayables.report_unpayables',
        'schedule': crontab(minute=0, hour='4'),
    },
    'delivere_to_child': {
        'task': 'say.tasks.delivere_to_child.delivere_to_child',
        'schedule': crontab(minute='10,40'),
    },
    'update_nakama_txs': {
        'task': 'say.tasks.nakama.update_nakama_txs',
        'schedule': 10 * 60,
    },
    'check_unverified_payments': {
        'task': 'say.tasks.check_unverified_payments.check_unverified_payments',
        'schedule': crontab(minute=59),
    },
}


def create_celery_app(beat):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param beat: celery beat object
    :return: Celery app
    """
    celery = Celery(
        'SAY',
        broker=configs.broker_url,
        include=CELERY_TASK_LIST,
    )
    celery.conf.beat_schedule = beat
    celery.conf.update(configs.to_dict())
    celery.conf.acksa_late = True

    celery.conf.task_default_priority = 5

    exchange = Exchange('celery')

    celery.conf.task_queues = [
        Queue(
            'celery',
            exchange,
            routing_key='celery',
            queue_arguments={'x-max-priority': 10},
        ),
        Queue(
            'slow', exchange, routing_key='slow', queue_arguments={'x-max-priority': 1}
        ),
    ]

    TaskBase = celery.Task

    db = create_engine(configs.postgres_url, pool_pre_ping=True)
    session_factory = sessionmaker(
        db,
        autoflush=False,
        autocommit=False,
        expire_on_commit=True,
        twophase=False,
    )
    session = scoped_session(session_factory)

    class DBTask(TaskBase):
        _session = None

        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        def after_return(self, *args, **kwargs):
            if self.session:
                self.session.remove()

            super().after_return(*args, **kwargs)

        @property
        def session(self):
            if self._session is None:
                self._session = session

            if not self._session.bind:
                engine = create_engine(url=configs.postgres_url)
                init_model(engine)

            return self._session

    celery.DBTask = DBTask

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            from say.app import app as flask_app

            with flask_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    setup_sentry()
    return celery


celery = create_celery_app(beat)
