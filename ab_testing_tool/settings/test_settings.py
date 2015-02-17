from .base import *

# NOTE: when running tests DEBUG mode is enabled regardless of setting it explicitly to False

# To disable logging during test runs, we add a null handler and
# set each logger's handler to it.
if not ENV_SETTINGS.get('enable_test_logging'):
    # Add a null log handler
    LOGGING['handlers']['null'] = {
        'class': 'logging.NullHandler'
    }
    for logger in LOGGING['loggers']:
        LOGGING['loggers'][logger]['handlers'] = ['null']
