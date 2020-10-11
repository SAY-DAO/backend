from kombu import Exchange, Queue
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from celery import Celery
from celery.schedules import crontab
from say.api import app as flask_app
from say.config import configs

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
        'schedule': crontab(minute=30, hour='4,16,0,8,12'),
    },
    'report_to_family': {
        'task': 'say.tasks.report_to_family.report_to_families',
        'schedule': crontab(minute=30, hour='3'),
    },
    'report_unpayables': {
        'task': 'say.tasks.report_unpayables.report_unpayables',
        'schedule': crontab(minute=0, hour='4'),
    },
    'delivere_to_child': {
        'task': 'say.tasks.delivere_to_child.delivere_to_child',
        'schedule': crontab(minute=0),
    },
}


def create_celery_app(beat):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param app: Flask app
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
            queue_arguments={'x-max-priority': 10}
        ),
        Queue(
            'slow', 
            exchange,
            routing_key='slow',
            queue_arguments={'x-max-priority': 1}
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
        def __init__(self, *args, **kwargs) -> None:
            self.session = session
            super().__init__(*args, **kwargs)

        def after_return(self, *args, **kwargs):
            if self.session:
                self.session.remove()
                
            super().after_return(*args, **kwargs)
            

    celery.DBTask = DBTask

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = create_celery_app(beat)
