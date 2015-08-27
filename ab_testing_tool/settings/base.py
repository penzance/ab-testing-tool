"""
Django settings for ab_testing_tool project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings
"""
import os
import logging
from .secure import SECURE_SETTINGS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECURE_SETTINGS.get('django_secret_key', 'changeme')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SECURE_SETTINGS.get('enable_debug', False)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_auth_lti',
    'django_canvas_oauth',
    'ab_tool',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cached_auth.Middleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Disabling this removes the need for @xframe_options_exempt on views
    # TODO: determine if there is a better way to prevent clickjacking within an iframe context
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_auth_lti.middleware.LTIAuthMiddleware',
    'error_middleware.middleware.ErrorMiddleware',
    'django_canvas_oauth.middleware.OAuthMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'ab_testing_tool.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.normpath(os.path.join(BASE_DIR, 'ab_testing_tool', 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'ab_testing_tool.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'ab_testing_tool'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'postgres'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),  # Default postgres port
    }
}

# Cache
# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES

REDIS_HOST = SECURE_SETTINGS.get('redis_host', '127.0.0.1')
REDIS_PORT = SECURE_SETTINGS.get('redis_port', 6379)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        'KEY_PREFIX': 'ab_testing_tool',  # Provide a unique value for shared cache
        # See following for default timeout (5 minutes as of 1.7):
        # https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES-TIMEOUT
        'TIMEOUT': SECURE_SETTINGS.get('default_cache_timeout_secs', 300),
    },
}

# Sessions

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

SESSION_COOKIE_NAME = 'djsessionid'

# NOTE: This setting only affects the session cookie, not the expiration of the session
# being stored in the cache.  The session keys will expire according to the value of
# SESSION_COOKIE_AGE, which defaults to 2 weeks when no value is given.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
# A boolean that specifies whether Django's translation system should be enabled. This provides
# an easy way to turn it off, for performance. If this is set to False, Django will make some
# optimizations so as not to load the translation machinery.  NOTE: can be loaded when needed
# in templates
USE_I18N = False
# A boolean that specifies if localized formatting of data will be enabled by default or not.
# If this is set to True, e.g. Django will display numbers and dates using the format of the
# current locale.  NOTE: can be loaded when needed in templates
USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static'))

# Logging

_DEFAULT_LOG_LEVEL = SECURE_SETTINGS.get('log_level', logging.DEBUG)
_LOG_ROOT = SECURE_SETTINGS.get('log_root', '')

# Turn off default Django logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#disabling-logging-configuration
LOGGING_CONFIG = None

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Merge this with Django's default logging configuration
    'formatters': {
        'verbose': {
            'format': '%(levelname)s\t%(asctime)s.%(msecs)03dZ\t%(name)s:%(lineno)s\t%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s\t%(name)s:%(lineno)s\t%(message)s',
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.handlers.WatchedFileHandler',
            'level': _DEFAULT_LOG_LEVEL,
            'formatter': 'verbose',
            'filename': os.path.join(_LOG_ROOT, 'django-ab_testing_tool.log'),
        },
    },
    # This is the default logger for any apps or libraries that use the logger
    # package, but are not represented in the `loggers` dict below.  A level
    # must be set and handlers defined.  Setting this logger is equivalent to
    # setting and empty string logger in the loggers dict below, but the separation
    # here is a bit more explicit.  See link for more details:
    # https://docs.python.org/2.7/library/logging.config.html#dictionary-schema-details
    'root': {
        'level': logging.WARNING,
        'handlers': ['default'],
    },
    'loggers': {
        'ab_tool': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
        'django_canvas_oauth': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
        'error_middleware': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        }
    },
}

# Currently deployed environment
ENV_NAME = SECURE_SETTINGS.get('env_name', 'local')

# Other app specific settings

# renderable_error.html is the default template specified in error_middleware and can be changed if desired
RENDERABLE_ERROR_TEMPLATE = "renderable_error.html"
# oauth_error.html is the default template specified in django_canvas_oauth and can be changed if desired
OAUTH_ERROR_TEMPLATE = "oauth_error.html"

CANVAS_OAUTH_CLIENT_ID = SECURE_SETTINGS.get('client_id')
CANVAS_OAUTH_CLIENT_SECRET = SECURE_SETTINGS.get('client_secret')

LTI_OAUTH_CREDENTIALS = SECURE_SETTINGS.get('lti_oauth_credentials', None)

COURSE_ACTIVE_DAYS = 365
NOTIFICATION_FREQUENCY_HOURS = 24

MAX_FILE_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# Email address that error messages come from
# See Django doc for current default value at:
# https://docs.djangoproject.com/en/[version]/ref/settings/#std:setting-SERVER_EMAIL
SERVER_EMAIL = SECURE_SETTINGS.get('email_server_email', 'root@localhost')
# Email address used in send_mail if no from address is specified, see
# See Django doc for current default value at:
# https://docs.djangoproject.com/en/[version]/ref/settings/#std:setting-DEFAULT_FROM_EMAIL
DEFAULT_FROM_EMAIL = SECURE_SETTINGS.get('email_default_from_email', 'webmaster@localhost')
