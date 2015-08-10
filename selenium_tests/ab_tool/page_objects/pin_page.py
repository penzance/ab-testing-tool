from selenium_tests.pin.page_objects.pin_page import PinLoginPageObject

class LoginPage(PinLoginPageObject):

    def login(self, username, password):
        """
        override the login method to return the correct page object.
        note that super must be called to do the actual login.
        """
        super(LoginPage, self).login(username, password)
        print 'Pin Login page returning Index page for user: %s' % username
       


