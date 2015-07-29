
###This is the page object model (POM) on the Main Page of AB Tool.  
from selenium.webdriver.common.by import By
from selenium_tests.ab_tool.page_objects.ab_base import ABBasePage
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

# These are page specific locators
class Locator1(object):
	_newexperiment = (By.LINK_TEXT, "New Experiment") 
	_h1_selector = (By.CSS_SELECTOR, "h1")	
	_name_loc = (By.CSS_SELECTOR, "h3.panel-title.panel-title-experiment")
	_delete_button = (By.CSS_SELECTOR, "[data-selenium-experiment-name='delete_MyExperiment']")
	_delete_confirm = (By.CSS_SELECTOR, "[data-selenium-experiment-name='confirm_delete_MyExperiment']")


class MainPage(ABBasePage):

    def get_title(self):
        """This gets the title of the page you're on to validate the right page loaded"""
        element = self.find_element(*Locator1._h1_selector)
        print 'title = %s' % element.text
        return element

    def click_to_create_experiment(self):
        """This clicks on the create experiment link on the mainpage"""
        create_experiment = self.find_element(*Locator1._newexperiment)
        create_experiment.click()


    def delete_experiment(self):
        """This clicks on the delete_experiment button on the main page"""
        delete_button = self.find_element(*Locator1._delete_button)
        delete_button.click()


    def delete_confirm (self):
        """This clicks on the confirm delete of experiment on the modal window"""
        delete_confirm = self.find_element(*Locator1._delete_confirm)
        delete_confirm.click()
