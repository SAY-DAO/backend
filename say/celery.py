from celery.schedules import crontab


beat = {
    'report-to-ngos': {
        'task': 'say.tasks.report_to_ngo.report_to_ngos',
        'schedule': crontab(minute=0, hour=9),
    },
    'update-needs': {
        'task': 'say.tasks.update_needs.update_needs',
        'schedule': crontab(minute=0, hour='8,20'),
    },
    'report_to_family': {
        'task': 'say.tasks.report_to_family.report_to_families',
        'schedule': crontab(minute=0, hour='23'),
    },
}

