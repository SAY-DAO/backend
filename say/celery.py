from celery.schedules import crontab


beat = {
    'report-to-ngos': {
        'task': 'say.tasks.report_to_ngo.report_to_ngos',
        'schedule': 5 * 60#crontab(minute=0, hour=23),
    },
    'update-needs': {
        'task': 'say.tasks.update_needs.update_needs',
        'schedule': 10#crontab(minute=0, hour=23),
    },
}

