from celery.schedules import crontab

OUTBOUND_PROXY = None  # for both http/https e.g.'http://127.0.0.1:8080'

ALEMBIC_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# specify where the token can be used
TOKEN_AUDIENCE = 'localhost'

# secret to make token signature
ACCESS_TOKEN_SECRET = 'this_is_not_secrettt'
REFRESH_TOKEN_SECRET = 'this_is_also_not_secrettt'

ACCESS_TOKEN_LIFETIME_SECS = 60 * 60
REFRESH_TOKEN_LIFETIME_SECS = 60 * 24 * 60 * 60

CLIENT_CERT_NAME_PREFIX = ''

# new refresh token is generated before expiry
REFRESH_TOKEN_EXTEND_SECS = 12 * 60 * 60

# CORS
ALLOW_ORIGINS = []

# Redis
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB_NUMBER = 7
AUTH_REDIS_HOST = 'localhost'
AUTH_REDIS_PORT = 6379
AUTH_REDIS_DB_NUMBER = 0

# AWS
AWS_ACCESS_KEY_ID = 'AAA'
AWS_ACCESS_SECRET = 'BBB'

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
CELERY_DEFAULT_EXCHANGE = 'atom:tarsier'
CELERY_DEFAULT_ROUTING_KEY = 'atom:tarsier'
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

# GRID config
GRID_URI = 'http://52.8.123.9:8084'
GRID_CACHE_TIMEOUT = 86400
REPORT_MAIL_SENDER = 'noreply@atom.trendmicro.com'

# HIPS config
API_CACHE_TIMEOUT = 3600

# 2 way ssl headers
SSL_HEADERS = ['X-Atom-Ssl-Verified', 'X-Atom-Ssl-Dn']

AWS_S3_HIPS_BUCKET_ID = ''

# enable this option to add a default schedule after baseline upload
ADD_DEFAULT_SCHEDULE = False

# baseline lock time
# unit: secs (-1 == forever)
UPLOAD_BASELINE_LOCK_TIMEOUT = -1

ENABLE_SCHEDULED_REPORT_MAIL = False

PDM_SERVER_HOST = 'http://localhost:1234'

# Limit File Upload Size
# MAX_CONTENT_LENGTH = ( 30 * 1024 * 1024 )
MAX_CONTENT_LENGTH = 31457280
