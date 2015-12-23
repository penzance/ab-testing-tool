from .base import *
from logging.config import dictConfig

ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For local development, allow setting a token in ENV_SETTINGS
COURSE_OAUTH_TOKEN = SECURE_SETTINGS.get("course_oauth_token")

INSTALLED_APPS += ('debug_toolbar', 'sslserver')

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

SELENIUM_CONFIG = {
    'selenium_username': SECURE_SETTINGS.get('selenium_user'),
    'selenium_password': SECURE_SETTINGS.get('selenium_password'),
    'selenium_grid_url': SECURE_SETTINGS.get('selenium_grid_url'),
    'base_url': 'https://canvas.dev.tlt.harvard.edu',
}

# Log to console instead of a file when running locally
LOGGING['handlers']['default'] = {
    'level': logging.DEBUG,
    'class': 'logging.StreamHandler',
    'formatter': 'simple',
}

dictConfig(LOGGING)
