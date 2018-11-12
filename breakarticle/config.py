from celery.schedules import crontab

OUTBOUND_PROXY = None  # for both http/https e.g.'http://127.0.0.1:8080'

ALEMBIC_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB_NUMBER = 7
AUTH_REDIS_HOST = 'localhost'
AUTH_REDIS_PORT = 6379
AUTH_REDIS_DB_NUMBER = 0

# Worker
CELERY_DISABLED = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/7'
CELERY_IGNORE_RESULT = True
CELERY_TIMEZONE = 'utc'
CELERY_ENABLE_UTC = True
CELERYD_HIJACK_ROOT_LOGGER = False
CELERY_ACCEPT_CONTENT = ['json']
CELERY_DEFAULT_QUEUE = 'atom:tarsier'
CELERYBEAT_SCHEDULE = {
    'sysinfo-scheduler': {
        'task': 'atomtarsier.tasks.start_sysinfo_gen_report_scheduler',
        'schedule': crontab(minute='*/5'),
        'args': (),
    },
    'hips-scheduler': {
        'task': 'atomtarsier.tasks.notify_virtual_patch_gradually',
        'schedule': crontab(minute='*'),
        'args': (),
    },

}

# enable this option to add a default schedule after baseline upload
ADD_DEFAULT_SCHEDULE = False
