#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    settings_module = "test_settings" if "test" in sys.argv else "local"
    settings_path = "ab_testing_tool.settings." + settings_module
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_path)
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
