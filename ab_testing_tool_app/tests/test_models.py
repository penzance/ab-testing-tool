from mock import patch

from ab_testing_tool_app.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_testing_tool_app.models import CourseSetting


class test_controllers(SessionTestCase):
    def test_get_finalized_course_does_not_exist(self):
        """ Tests that get_finalized works when the course settings don't exist
            yet for the course """
        self.assertFalse(CourseSetting.get_is_finalized(TEST_COURSE_ID))
    
    def test_get_finalized_course_exists(self):
        """ Tests that get_finalized works when the course settings already
            exist for the course """
        CourseSetting.objects.create(course_id=TEST_COURSE_ID)
        self.assertFalse(CourseSetting.get_is_finalized(TEST_COURSE_ID))
    
    def test_set_finalized_course_does_not_exist(self):
        """ Tests that set finalized changes the return of get_finalized to
            true, and succeeds when the course settings don't yet exist """
        CourseSetting.set_finalized(TEST_COURSE_ID)
        self.assertTrue(CourseSetting.get_is_finalized(TEST_COURSE_ID))
    
    def test_set_finalized_course_exists(self):
        """ Tests that set finalized changes the return of get_finalized to
            true, and succeeds when the course settings already exist """
        CourseSetting.objects.create(course_id=TEST_COURSE_ID)
        CourseSetting.set_finalized(TEST_COURSE_ID)
        self.assertTrue(CourseSetting.get_is_finalized(TEST_COURSE_ID))
    
    def test_get_finalized_idempotent(self):
        """ Tests that get_finalized doesn't change the value of is_finalized """
        self.assertFalse(CourseSetting.get_is_finalized(TEST_COURSE_ID))
        self.assertFalse(CourseSetting.get_is_finalized(TEST_COURSE_ID))
        CourseSetting.set_finalized(TEST_COURSE_ID)
        self.assertTrue(CourseSetting.get_is_finalized(TEST_COURSE_ID))
        self.assertTrue(CourseSetting.get_is_finalized(TEST_COURSE_ID))
