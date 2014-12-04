from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

STATIC_ROOT = normpath(join(SITE_ROOT, 'http_static'))

LOGGING = {
    'version': 1,
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'ab_tool': {
            'handlers':['null'],
            'propagate': True,
            'level':'DEBUG',
        },
        'error_middleware': {
            'handlers':['null'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
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
