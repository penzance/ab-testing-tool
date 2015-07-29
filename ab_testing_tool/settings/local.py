from .base import *

INSTALLED_APPS += ('debug_toolbar', 'sslserver')

SELENIUM_CONFIG = {
   'selenium_username': ENV_SETTINGS.get('selenium_user'),
   'selenium_password': ENV_SETTINGS.get('selenium_password'),
   'selenium_grid_url': ENV_SETTINGS.get('selenium_grid_url'),
   'base_url': 'https://canvas.icommons.harvard.edu',
}