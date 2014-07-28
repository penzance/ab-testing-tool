from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

STATIC_ROOT = normpath(join(SITE_ROOT, 'http_static'))
