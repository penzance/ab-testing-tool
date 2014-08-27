from ab_testing_tool_app.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_testing_tool_app.models import CourseSetting, Track, Stage, StageUrl


class TestModels(SessionTestCase):
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
    
    def test_get_returns_none(self):
        """ Tests that get_or_none returns None when object does not exist"""
        stage = Stage.objects.create(course_id=TEST_COURSE_ID, name="stage")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        self.assertIsNone(StageUrl.get_or_none(stage=stage, track=track1))

    def test_is_missing_urls_true(self):
        """ Tests that is_missing_urls returns false when a url is missing """
        stage = Stage.objects.create(course_id=TEST_COURSE_ID, name="stage")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        Track.objects.create(course_id=TEST_COURSE_ID, name="track2")
        StageUrl.objects.create(stage=stage, track=track1, url="example.com")
        self.assertTrue(stage.is_missing_urls())
    
    def test_is_missing_urls_true_no_url(self):
        """ Tests that is_missing_urls returns true when not all urls have urls """
        stage = Stage.objects.create(course_id=TEST_COURSE_ID, name="stage")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        StageUrl.objects.create(stage=stage, track=track1)
        self.assertTrue(stage.is_missing_urls())
    
    def test_is_missing_urls_true_blank_url(self):
        """ Tests that is_missing_urls returns true when not all urls are filled in """
        stage = Stage.objects.create(course_id=TEST_COURSE_ID, name="stage")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        StageUrl.objects.create(stage=stage, track=track1, url="")
        self.assertTrue(stage.is_missing_urls())
    
    def test_is_missing_urls_false(self):
        """ Tests that is_missing_urls returns false when all urls are filled """
        stage = Stage.objects.create(course_id=TEST_COURSE_ID, name="stage")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        track2 = Track.objects.create(course_id=TEST_COURSE_ID, name="track2")
        StageUrl.objects.create(stage=stage, track=track1, url="http://example.com")
        StageUrl.objects.create(stage=stage, track=track2, url="http://example.com")
        self.assertFalse(stage.is_missing_urls())
