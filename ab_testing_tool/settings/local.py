from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# This is for https forwarding on server
# SECURITY WARNING: https://docs.djangoproject.com/en/1.7/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

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
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple',
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
        'ab_testing_tool': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
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
