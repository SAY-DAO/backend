from celery.schedules import crontab


beat = {
    'report-to-social-workers': {
        'task': 'say.tasks.report_to_social_worker.report_to_social_workers',
        'schedule': 5 * 60 #crontab(minute=30, hour='2,9'),
    },
    'update-needs': {
        'task': 'say.tasks.update_needs.update_needs',
        'schedule': crontab(minute=30, hour='4,16,0,8,12'),
    },
    'report_to_family': {
        'task': 'say.tasks.report_to_family.report_to_families',
        'schedule': 60# crontab(minute=30, hour='3'),
    },
}

