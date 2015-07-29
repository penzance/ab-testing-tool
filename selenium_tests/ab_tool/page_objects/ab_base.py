

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
from abc import abstractmethod
from selenium_tests.base_page_object import BasePageObject


###This is the base class that all page models can inherit from###

class ABBasePage(BasePageObject):
 
    def __init__(self, driver):
        self._driver = driver
        try:
            self._driver.switch_to.frame(self._driver.find_element_by_id("tool_content"))
        except NoSuchElementException:
            pass

        
    #@abstractmethod
    def _validate_page(self, driver):
        return

    def find_element(self, *loc):
        return self._driver.find_element(*loc)

    def find_elements(self, *loc):
        return self._driver.find_elements(*loc)


class InvalidPageException(Exception):
    """ Throw this exception when you don't find the correct page """
    pass



