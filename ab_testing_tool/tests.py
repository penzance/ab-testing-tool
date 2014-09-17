import os
from django.core.exceptions import ImproperlyConfigured
from unittest import TestCase
from ab_testing_tool.settings.base import get_env_variable

class TestSettings(TestCase):
    def test_get_env_variable(self):
        os.environ.setdefault("VAR_NAME", "var_value")
        self.assertEqual(get_env_variable("VAR_NAME"), "var_value")
    
    def test_get_env_variable_raises_exception(self):
        if os.environ.has_key("VAR_NAME"):
            os.environ.pop("VAR_NAME")
        self.assertRaises(ImproperlyConfigured, get_env_variable, "VAR_NAME")