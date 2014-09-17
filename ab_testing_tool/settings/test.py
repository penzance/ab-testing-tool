from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

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
        'ab_testing_tool_app': {
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
