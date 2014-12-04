from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

STATIC_ROOT = normpath(join(SITE_ROOT, 'http_static'))

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        }
    },
    'handlers': {
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/opt/tlt/logs/ab_testing_tool.log',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
     },
    'loggers': {
        'django.request': {
            'handlers':['console'],
            'propagate': True,
            'level':'DEBUG',
        },
        'django_auth_lti': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG'
        },
        'ab_tool': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'error_middleware': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        }
    },
}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'django-qa-cache.kc9kh3.0001.use1.cache.amazonaws.com:6379',
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
    },
}

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_HOST = 'django-qa-cache.kc9kh3.0001.use1.cache.amazonaws.com'
SESSION_REDIS_PORT = 6379

SESSION_COOKIE_SECURE = True
