from celery.schedules import crontab


beat = {
    'report-to-ngos': {
        'task': 'say.tasks.report_to_ngo.report_to_ngos',
        'schedule': 3 * 60#crontab(minute=0, hour=23),
    },
    'update-needs': {
        'task': 'say.tasks.update_needs.update_needs',
        'schedule': 60 * 60#crontab(minute=0, hour=23),
    },
}

