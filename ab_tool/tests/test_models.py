from ab_tool.tests.common import SessionTestCase, TEST_COURSE_ID
from ab_tool.models import CourseSettings, Track, InterventionPoint, InterventionPointUrl


class TestModels(SessionTestCase):
    def test_get_finalized_course_does_not_exist(self):
        """ Tests that get_finalized works when the course settings don't exist
            yet for the course """
        self.assertFalse(CourseSettings.get_is_finalized(TEST_COURSE_ID))
    
    def test_get_finalized_course_exists(self):
        """ Tests that get_finalized works when the course settings already
            exist for the course """
        CourseSettings.objects.create(course_id=TEST_COURSE_ID)
        self.assertFalse(CourseSettings.get_is_finalized(TEST_COURSE_ID))
    
    def test_is_finalized_course_finalized(self):
        """ Tests that get_finalized true when the course settings already
            finalized for the course """
        CourseSettings.objects.create(course_id=TEST_COURSE_ID,
                                     tracks_finalized=True)
        self.assertTrue(CourseSettings.get_is_finalized(TEST_COURSE_ID))
    
    def test_set_finalized_sets_true(self):
        """ Tests that set finalized changes the tracks_finalized property of
            the appropriate course to true """
        CourseSettings.set_finalized(TEST_COURSE_ID)
        course_setting = CourseSettings.objects.get(course_id=TEST_COURSE_ID)
        self.assertTrue(course_setting.tracks_finalized)
    
    def test_set_finalized_course_does_not_exist(self):
        """ Tests that set finalized changes the return of get_finalized to
            true, and succeeds when the course settings don't yet exist """
        CourseSettings.set_finalized(TEST_COURSE_ID)
        course_setting = CourseSettings.objects.get(course_id=TEST_COURSE_ID)
        self.assertTrue(course_setting.tracks_finalized)
    
    def test_set_finalized_course_exists(self):
        """ Tests that set finalized changes is_finalized to True
            when the course settings already exist """
        CourseSettings.objects.create(course_id=TEST_COURSE_ID,
                                     tracks_finalized=False)
        CourseSettings.set_finalized(TEST_COURSE_ID)
        course_setting = CourseSettings.objects.get(course_id=TEST_COURSE_ID)
        self.assertTrue(course_setting.tracks_finalized)
    
    def test_set_finalized_course_finalized(self):
        """ Tests that set finalized leaves is_finalized as True
            when the course settings already exist """
        CourseSettings.objects.create(course_id=TEST_COURSE_ID,
                                     tracks_finalized=True)
        CourseSettings.set_finalized(TEST_COURSE_ID)
        course_setting = CourseSettings.objects.get(course_id=TEST_COURSE_ID)
        self.assertTrue(course_setting.tracks_finalized)
    
    def test_set_finalized_idempotent(self):
        """ Tests that set_finalized can be called multiple times and
            have the outcome the same as if it were called once """
        CourseSettings.objects.create(course_id=TEST_COURSE_ID,
                                     tracks_finalized=False)
        CourseSettings.set_finalized(TEST_COURSE_ID)
        course_setting = CourseSettings.objects.get(course_id=TEST_COURSE_ID)
        self.assertTrue(course_setting.tracks_finalized)
        CourseSettings.set_finalized(TEST_COURSE_ID)
        course_setting = CourseSettings.objects.get(course_id=TEST_COURSE_ID)
        self.assertTrue(course_setting.tracks_finalized)
    
    def test_get_finalized_idempotent(self):
        """ Tests that get_finalized doesn't change the value of is_finalized """
        self.assertFalse(CourseSettings.get_is_finalized(TEST_COURSE_ID))
        self.assertFalse(CourseSettings.get_is_finalized(TEST_COURSE_ID))
        CourseSettings.set_finalized(TEST_COURSE_ID)
        self.assertTrue(CourseSettings.get_is_finalized(TEST_COURSE_ID))
        self.assertTrue(CourseSettings.get_is_finalized(TEST_COURSE_ID))
    
    def test_is_missing_urls_true(self):
        """ Tests that is_missing_urls returns false when a url is missing """
        intervention_point = InterventionPoint.objects.create(course_id=TEST_COURSE_ID, name="intervention_point")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        Track.objects.create(course_id=TEST_COURSE_ID, name="track2")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1, url="example.com")
        self.assertTrue(intervention_point.is_missing_urls())
    
    def test_is_missing_urls_true_no_url(self):
        """ Tests that is_missing_urls returns true when not all urls have urls """
        intervention_point = InterventionPoint.objects.create(course_id=TEST_COURSE_ID, name="intervention_point")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1)
        self.assertTrue(intervention_point.is_missing_urls())
    
    def test_is_missing_urls_true_blank_url(self):
        """ Tests that is_missing_urls returns true when not all urls are filled in """
        intervention_point = InterventionPoint.objects.create(course_id=TEST_COURSE_ID, name="intervention_point")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1, url="")
        self.assertTrue(intervention_point.is_missing_urls())
    
    def test_is_missing_urls_false(self):
        """ Tests that is_missing_urls returns false when all urls are filled """
        intervention_point = InterventionPoint.objects.create(course_id=TEST_COURSE_ID, name="intervention_point")
        track1 = Track.objects.create(course_id=TEST_COURSE_ID, name="track1")
        track2 = Track.objects.create(course_id=TEST_COURSE_ID, name="track2")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track1, url="http://example.com")
        InterventionPointUrl.objects.create(intervention_point=intervention_point, track=track2, url="http://example.com")
        self.assertFalse(intervention_point.is_missing_urls())
