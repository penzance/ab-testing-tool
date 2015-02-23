"""
Django settings for ab_testing_tool project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import os
from os.path import abspath, basename, dirname, join, normpath
from sys import path
from .secure import SECURE_SETTINGS as ENV_SETTINGS

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = dirname(dirname(__file__))

### Path stuff as recommended by Two Scoops / with local mods

# Absolute filesystem path to the Django project config directory:
# (this is the parent of the directory where this file resides,
# since this file is now inside a 'settings' pacakge directory)
DJANGO_PROJECT_CONFIG = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
# (this is one directory up from the project config directory)
SITE_ROOT = dirname(DJANGO_PROJECT_CONFIG)

# Site name:
SITE_NAME = basename(SITE_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(SITE_ROOT)

### End path stuff

# THESE ADDRESSES WILL RECEIVE EMAIL ABOUT CERTAIN ERRORS!
ADMINS = ()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENV_SETTINGS.get('django_secret_key', 'changeme')

LTI_OAUTH_CREDENTIALS = ENV_SETTINGS.get('lti_oauth_credentials', None)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV_SETTINGS.get('enable_debug', False)

TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_canvas_oauth',
    'ab_tool',
    'gunicorn',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Disabling these removes the need for @xframe_options_exempt, @csrf_exempt on views
    # TODO: determine if this is a better way to go about this
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_auth_lti.middleware.LTIAuthMiddleware',
    'error_middleware.middleware.ErrorMiddleware',
    'django_canvas_oauth.middleware.OAuthMiddleware'
)

AUTHENTICATION_BACKENDS = (
    'django_auth_lti.backends.LTIAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'ab_testing_tool.urls'

WSGI_APPLICATION = 'ab_testing_tool.wsgi.application'

# Database settings
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
_DB_SETTINGS = ENV_SETTINGS.get('database')
if _DB_SETTINGS:
    # Using postgres for this project
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': _DB_SETTINGS.get('name'),
            'USER': _DB_SETTINGS.get('user'),
            'PASSWORD': _DB_SETTINGS.get('password'),
            'HOST': _DB_SETTINGS.get('host', '127.0.0.1'),
            'PORT': _DB_SETTINGS.get('port', 5432),
        }
    }
else:  # Default to sqlite db
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/ab-testing/static/'

STATIC_ROOT = normpath(join(SITE_ROOT, 'http_static'))

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# renderable_error.html is the default template specified in error_middleware and can be changed if desired
RENDERABLE_ERROR_TEMPLATE = "renderable_error.html"
# oauth_error.html is the default template specified in django_canvas_oauth and can be changed if desired
OAUTH_ERROR_TEMPLATE = "oauth_error.html"

CANVAS_OAUTH_CLIENT_ID = ENV_SETTINGS.get('client_id')
CANVAS_OAUTH_CLIENT_SECRET = ENV_SETTINGS.get('client_secret')

# This is for https forwarding on server
# SECURITY WARNING: https://docs.djangoproject.com/en/1.7/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if ENV_SETTINGS.get('redis_cache_host'):
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': ENV_SETTINGS.get('redis_cache_host'),
            'OPTIONS': {
                'PARSER_CLASS': 'redis.connection.HiredisParser'
            },
        },
    }

if ENV_SETTINGS.get('redis_sessions_host'):
    SESSION_ENGINE = 'redis_sessions.session'
    SESSION_REDIS_HOST = ENV_SETTINGS.get('redis_sessions_host', 'localhost')
    SESSION_REDIS_PORT = ENV_SETTINGS.get('redis_sessions_port', 6379)

# Django defaults to False (as of 1.7)
SESSION_COOKIE_SECURE = ENV_SETTINGS.get('use_secure_cookies', False)

# session cookie lasts for 7 hours (in seconds)
SESSION_COOKIE_AGE = 60 * 60 * 7

SESSION_COOKIE_NAME = 'djsessionid'

SESSION_COOKIE_HTTPONLY = True

_DEFAULT_LOG_LEVEL = ENV_SETTINGS.get('log_level', 'DEBUG')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # Merge this with Django's default logging configuration
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        }
    },
    # Borrowing some default filters for app loggers
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        # In case we turn on mail for any of the below loggers
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        # For testing purposes and fallback for mail filter
        'null': {
            'class': 'logging.NullHandler',
        },
        'logfile': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': join(ENV_SETTINGS.get('log_root', ''), 'ab_testing_tool.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django_auth_lti': {
            'handlers': ['console', 'logfile'],
            'level': _DEFAULT_LOG_LEVEL,
        },
        'ab_tool': {
            'handlers': ['console', 'logfile', 'mail_admins'],
            'level': _DEFAULT_LOG_LEVEL,
        },
        'error_middleware': {
            'handlers': ['console', 'logfile'],
            'level': _DEFAULT_LOG_LEVEL,
        }
    },
}
