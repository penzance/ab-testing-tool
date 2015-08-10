"""
To run these tests from the command line in a local VM, you'll need to set up the environment:
> export PYTHONPATH=/home/vagrant/icommons_lti_tools
> export DJANGO_SETTINGS_MODULE=icommons_lti_tools.settings.local
> sudo apt-get install xvfb
> python selenium_tests/regression_tests.py

Or for just one set of tests, for example:
> python selenium_tests/manage_people/mp_test_search.py

In PyCharm, if xvfb is installed already, you can run them through the Python unit test run config
(make sure the above environment settings are included)
"""

import unittest
import time
from selenium_tests.ab_tool.ab_tests import test_ab_tool
import HTMLTestRunner


date_timestamp = time.strftime('%Y%m%d_%H_%M_%S')


buf = file("TestReport" + "_" + date_timestamp + ".html", 'wb')
runner = HTMLTestRunner.HTMLTestRunner(
    stream=buf,
    title='Test the Report',
    description='Result of tests'
)

ab_tests = unittest.TestLoader().loadTestsFromTestCase(test_ab_tool)
# create a test suite combining search_tests and results_page_tests

smoke_tests = unittest.TestSuite([ab_tests])

# run the suite
runner.run(smoke_tests)
# close test report file
buf.close()


