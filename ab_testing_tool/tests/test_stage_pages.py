from django.conf import settings
from django.core.urlresolvers import reverse
from mock import patch

from ab_testing_tool.pages.main_pages import STAGE_URL_TAG
from ab_testing_tool.controllers import (get_uninstalled_stages,
    stage_url)
from ab_testing_tool.models import Stage, StageUrl, Track
from ab_testing_tool.tests.test_main_pages import (SessionTestCase,
    TEST_COURSE_ID, APIReturn, LIST_MODULES, LIST_ITEMS)


class test_stage_pages(SessionTestCase):
    """Tests related to Stages and Stage-related pages and methods"""

    def test_create_stage_view(self):
        """Tests edit_stage template renders for url 'create_stage' when authenticated"""
        response = self.client.get(reverse("create_stage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")

    def test_create_stage_view_unauthorized(self):
        """Tests edit_stage template renders for url 'create_stage' when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("create_stage"))
        self.assertTemplateNotUsed(response, "edit_stage.html")

    def test_edit_stage_view(self):
        """Tests edit_stage template renders when authenticated"""
        stage = Stage.objects.create(name="stage1")
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")

    def test_edit_stage_view_unauthorized(self):
        """Tests edit_stage template renders when unauthorized"""
        self.set_roles([])
        stage = Stage.objects.create(name="stage1")
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)))
        self.assertTemplateNotUsed(response, "edit_stage.html")

    def test_deploy_stage_view(self):
        """Tests deploy stage"""
        stage = Stage.objects.create(name="stage1")
        track = Track.objects.create(name="track1")
        stage_url = StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        t_id = stage.id
        response = self.client.get(reverse("deploy_stage", args=(t_id,)), follow=True)
        self.assertEqual(response.status_code, 200)

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

    def test_submit_create_stage(self):
        #TODO: change this test to several tests that Stage and StageUrls in DB,
        #covering the cases when no stage urls submited, with stage urls are submitted
        """Tests that create_stage creates a Stage object verified by DB count"""
        num_stages = Stage.objects.count()
        data = {"name": "stage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages + 1, Stage.objects.count())

    def test_submit_create_stage_with_stageurls(self):
        """Tests that create_stage creates a Stage object and StageUrl objects
            verified by DB count"""
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        data = {"name": "stage", STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages + 1, Stage.objects.count())
        self.assertEquals(num_stageurls + 2, StageUrl.objects.count())

    def test_submit_edit_stage(self):
        """ Tests that edit_stage does not change DB count but does change Stage
            attribute"""
        stage = Stage.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        stage_id = stage.id
        num_stages = Stage.objects.count()
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(num_stages, Stage.objects.count())
        stage = Stage.objects.get(id=stage_id)
        self.assertEquals(stage.name, "new_name")

    def test_update_nonexistent_stage(self):
        """ Tests that update_stage method raises error for non-existent Stage """
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": 10000987}
        self.assertRaises(Exception, self.client.post,
                          reverse("submit_edit_stage"), data, follow=True)

    def test_submit_edit_stage_wrong_course(self):
        """ Tests that update_stage method raises error for existent Stage but
            for wrong course"""
        #TODO: make similar test for update_tracks
        #TODO: render template tests for all the forms
        stage = Stage.objects.create(name="old_name",
                                             course_id="other_course")
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage.id}
        self.assertRaises(Exception, self.client.post,
                          reverse("submit_edit_stage"), data, follow=True)
