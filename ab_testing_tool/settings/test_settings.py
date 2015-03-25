from .base import *

# NOTE: when running tests DEBUG mode is enabled regardless of setting it explicitly to False

# To disable logging during test runs, we add a null handler and
# set each logger's handler to it.
if not ENV_SETTINGS.get('enable_test_logging'):
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['null']

# make tests faster
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
    },
}
