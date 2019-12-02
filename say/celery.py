from celery.schedules import crontab


beat = {
    'report-to-ngos': {
        'task': 'say.tasks.report_to_ngo.report_to_ngos',
        'schedule': crontab(minute=0, hour=23),
    },
}

