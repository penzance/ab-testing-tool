from django.core.urlresolvers import reverse
from mock import patch

from ab_testing_tool.constants import STAGE_URL_TAG
from ab_testing_tool.models import Stage, StageUrl, Track
from ab_testing_tool.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_STAGE_ID, APIReturn, LIST_MODULES,
    LIST_ITEMS)
from ab_testing_tool.controllers import stage_url


class test_stage_pages(SessionTestCase):
    """Tests related to Stages and Stage-related pages and methods"""
    
    def test_create_stage_view(self):
        """Tests edit_stage template renders for url 'create_stage' when authenticated"""
        response = self.client.get(reverse("create_stage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
    
    def test_create_stage_view_unauthorized(self):
        """Tests edit_stage template does not render for url 'create_stage' when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("create_stage"), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view(self):
        """Tests edit_stage template renders when authenticated"""
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
    
    def test_edit_stage_view_unauthorized(self):
        """Tests edit_stage template renders when unauthorized"""
        self.set_roles([])
        stage = Stage.objects.create(name="stage1")
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view_nonexistent(self):
        """Tests edit_stage template renders when stage does not exist"""
        t_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("edit_stage", args=(t_id,)), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "error.html")
    
    def test_edit_stage_view_wrong_course(self):
        """Tests edit_track when attempting to access a track from a different course"""
        stage = Stage.objects.create(name="stage1", course_id=TEST_OTHER_COURSE_ID)
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)))
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "error.html")
    
    def test_submit_create_stage(self):
        """Tests that create_stage creates a Stage object verified by DB count"""
        num_stages = Stage.objects.count()
        data = {"name": "stage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_stages + 1, Stage.objects.count())
    
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
        self.assertEqual(num_stages + 1, Stage.objects.count())
        self.assertEqual(num_stageurls + 2, StageUrl.objects.count())
    
    def test_submit_create_stage_unauthorized(self):
        """Tests that create_stage unauthorized"""
        self.set_roles([])
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        data = {"name": "stage", STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage", "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(num_stages, Stage.objects.count())
        self.assertEqual(num_stageurls, StageUrl.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
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
        self.assertEqual(num_stages, Stage.objects.count())
        stage = Stage.objects.get(id=stage_id)
        self.assertEqual(stage.name, "new_name")
    
    def test_submit_edit_stage_unauthorized(self):
        """ Tests that edit_stage when unauthorized"""
        self.set_roles([])
        stage = Stage.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        stage_id = stage.id
        num_stages = Stage.objects.count()
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(num_stages, Stage.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_edit_stage_nonexistent(self):
        """ Tests that update_stage method raises error for non-existent Stage """
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": NONEXISTENT_STAGE_ID}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertTemplateUsed(response, "error.html")
    
    def test_submit_edit_stage_wrong_course(self):
        """ Tests that update_stage method raises error for existent Stage but
            for wrong course"""
        stage = Stage.objects.create(name="old_name",
                                     course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage.id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertTemplateUsed(response, "error.html")
    
    def test_deploy_stage_view(self):
        """Tests deploy stage"""
        stage = Stage.objects.create(name="stage1")
        track = Track.objects.create(name="track1")
        StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        t_id = stage.id
        response = self.client.get(reverse("deploy_stage", args=(t_id,)), follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_stage(self):
        """ Tests that delete_stage method properly deletes a stage when authorized"""
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_stages + 1, Stage.objects.count())
        t_id = stage.id
        response = self.client.get(reverse("delete_stage", args=(t_id,)), follow=True)
        second_num_stages = Stage.objects.count()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_unauthorized(self):
        """ Tests that delete_stage method raises error when unauthorized"""
        self.set_roles([])
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        t_id = stage.id
        response = self.client.get(reverse("delete_stage", args=(t_id,)), follow=True)
        second_num_stages = Stage.objects.count()
        self.assertTemplateUsed(response, "not_authorized.html")
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_nonexistent(self):
        """ Tests that delete_stage method raises error for non-existent Stage"""
        first_num_stages = Stage.objects.count()
        Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        t_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("delete_stage", args=(t_id,)), follow=True)
        second_num_stages = Stage.objects.count()
        self.assertTemplateUsed(response, "error.html")
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_wrong_course(self):
        """ Tests that delete_stage method raises error for existent Stage but for
            wrong course"""
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_OTHER_COURSE_ID)
        t_id = stage.id
        response = self.client.get(reverse("delete_stage", args=(t_id,)), follow=True)
        second_num_stages = Stage.objects.count()
        self.assertTemplateUsed(response, "error.html")
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_delete_stage_installed(self, _mock1):
        """ Tests that delete_stage method when stage is installed"""
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_stages + 1, Stage.objects.count())
        t_id = stage.id
        mock_item = {"type": "ExternalTool",
                     "external_url": stage_url(self.request, t_id)}
        with patch(LIST_ITEMS, return_value=APIReturn([mock_item])):
            #TODO:
            #response = self.client.get(reverse("delete_stage", args=(t_id,)), follow=True)
            second_num_stages = Stage.objects.count()
            self.assertNotEqual(first_num_stages, second_num_stages)
            #self.assertTemplateUsed(response, "error.html")
