from .local import *

# NOTE: when running tests DEBUG mode is enabled regardless of setting it explicitly to False

# To disable logging during test runs, we add a null handler and
# set each logger's handler to it.
if not SECURE_SETTINGS.get('enable_test_logging'):
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['null']

# make tests faster
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'ab_testing_tool',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache'
    },
}
