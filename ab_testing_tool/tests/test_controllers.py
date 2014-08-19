from mock import patch

from ab_testing_tool.controllers import get_uninstalled_stages, stage_url
from ab_testing_tool.tests.common import (SessionTestCase, APIReturn,
    LIST_MODULES, LIST_ITEMS)
from ab_testing_tool.models import Stage


class test_stage_pages(SessionTestCase):
    
    def test_get_uninstalled_stages(self):
        """Tests method get_uninstalled_stages runs and returns no stages when database empty"""
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 0)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_with_item(self, _mock1):
        """Tests method get_uninstalled_stages returns one when database has one item"""
        #TODO !! take into account course_id here!!
        Stage.objects.create(name="stage1")
        stages = get_uninstalled_stages(self.request)
        self.assertEqual(len(stages), 1)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_get_uninstalled_stages_against_api(self, _mock1):
        """ Tests method get_uninstalled_stages returns zero when stage in database
            is also returned by the API, which means it is installed """
        stage = Stage.objects.create(name="stage1")
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, stage.id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            stages = get_uninstalled_stages(self.request)
            self.assertEqual(len(stages), 0)
