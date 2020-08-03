from celery import Celery
from celery.schedules import crontab

from say.config import config
from say.orm import session, create_engine, bind_session

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


def create_celery_app(app):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.
    :param app: Flask app
    :return: Celery app
    """
    app = app

    celery = Celery(app.import_name, broker=config['broker_url'],
                    include=CELERY_TASK_LIST)
    celery.conf.timezone = 'UTC'
    celery.conf.beat_schedule = beat
    celery.conf.update(config)

    TaskBase = celery.Task

    class DBTask(TaskBase):
        _session = None

        def after_return(self, *args, **kwargs):
            if self._session is not None:
                self._session.close()
                self._session.remove()

        @property
        def session(self):
            if self._session is None:
                self._session = session

            if not self._session.bind:
                engine = create_engine(url=config['dbUrl'])
                bind_session(engine)

            return self._session

    celery.DBTask = DBTask

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
