from mock import patch

from ab_testing_tool.controllers import get_uninstalled_stages, stage_url,\
    all_stage_urls
from ab_testing_tool.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS, TEST_COURSE_ID, TEST_OTHER_COURSE_ID)
from ab_testing_tool.models import Stage
from ab_testing_tool.exceptions import BAD_STAGE_ID


class test_controllers(SessionTestCase):
    def test_get_uninstalled_stages(self):
        """ Tests method get_uninstalled_stages runs and returns no stages when
            database empty """
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 0)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_with_item(self, _mock1):
        """ Tests method get_uninstalled_stages returns one when database has
            one item and api returns nothing """
        Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 1)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_against_courses(self, _mock1):
        """ Tests method get_uninstalled_stages returns one when database has
            two items but only one matches the course and api returns nothing """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        Stage.objects.create(name="stage2", course_id=TEST_OTHER_COURSE_ID)
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 1)
        self.assertSameIds([stage], stages)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_with_all_installed(self, _mock1):
        """ Tests method get_uninstalled_stages returns zero when stage in
            database is also returned by the API, which means it is installed """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, stage.id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            stages = get_uninstalled_stages(self.request)
            self.assertEqual(len(stages), 0)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_with_some_installed(self, _mock1):
        """ Tests method get_uninstalled_stages returns one when there are two
            stages in the database, one of which is also returned by the API,
            which means it is installed """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        Stage.objects.create(name="stage2", course_id=TEST_COURSE_ID)
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, stage.id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            stages = get_uninstalled_stages(self.request)
            self.assertEqual(len(stages), 1)
    
    def test_all_stage_urls_empty(self):
        """ Tests that all_stage_urls returns empty when there are no stages """
        urls = all_stage_urls(self.request, TEST_COURSE_ID)
        self.assertEqual(len(urls), 0)
    
    def test_all_stage_urls_one_element(self):
        """ Tests that all_stage_urls returns the url for one stage when
            that is in the database """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        urls = all_stage_urls(self.request, TEST_COURSE_ID)
        self.assertEqual(len(urls), 1)
        self.assertEqual([stage_url(self.request, stage.id)], urls)
    
    def test_all_stage_urls_multiple_courses(self):
        """ Tests that all_stage_urls only returns the url for the stage
            in the database that matches the course_id """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        Stage.objects.create(name="stage2", course_id=TEST_OTHER_COURSE_ID)
        urls = all_stage_urls(self.request, TEST_COURSE_ID)
        self.assertEqual(len(urls), 1)
        self.assertEqual([stage_url(self.request, stage.id)], urls)
    
    def test_stage_url_contains_stage_id(self):
        """ Tests that stage_url contains the string of the stage_id """
        stage_id = 999888777
        url = stage_url(self.request, stage_id)
        self.assertIn(str(stage_id), url)
    
    def test_stage_url_works_with_string_id(self):
        """ Tests that stage_url succeeds when stage_id is a number string """
        stage_id = "999888777"
        url = stage_url(self.request, stage_id)
        self.assertIn(stage_id, url)
    
    def test_stage_url_contains_host(self):
        """ Tests that stage_url's output contains the host of the request """
        stage_id = "1"
        url = stage_url(self.request, stage_id)
        self.assertIn(self.request.get_host(), url)
    
    def test_stage_url_errors(self):
        """ Tests that stage_url errors when passed a non-numeral stage_id """
        self.assertRaisesSpecific(BAD_STAGE_ID, stage_url, self.request, None)
        self.assertRaisesSpecific(BAD_STAGE_ID, stage_url, self.request, "str")
