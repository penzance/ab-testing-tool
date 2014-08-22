from django.core.urlresolvers import reverse

from ab_testing_tool.constants import STAGE_URL_TAG
from ab_testing_tool.models import Stage, StageUrl, Track
from ab_testing_tool.tests.common import SessionTestCase, TEST_COURSE_ID,\
    TEST_OTHER_COURSE_ID, NONEXISTANT_STAGE_ID
from ab_testing_tool.pages.stage_pages import delete_stage
from ab_testing_tool.exceptions import DELETING_INSTALLED_STAGE, MISSING_STAGE


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
        StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        t_id = stage.id
        response = self.client.get(reverse("deploy_stage", args=(t_id,)), follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_submit_create_stage(self):
        #TODO: change this test to several tests that Stage and StageUrls in DB,
        #covering the cases when no stage urls submited, with stage urls are submitted
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
    
    def test_update_nonexistent_stage(self):
        """ Tests that update_stage method raises error for non-existent Stage """
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": NONEXISTANT_STAGE_ID}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertTemplateUsed(response, "error.html")
    
    def test_submit_edit_stage_wrong_course(self):
        """ Tests that update_stage method raises error for existent Stage but
            for wrong course"""
        #TODO: make similar test for update_tracks
        #TODO: render template tests for all the forms
        stage = Stage.objects.create(name="old_name",
                                     course_id=TEST_OTHER_COURSE_ID)
        data = {"name": "new_name", "url1": "http://example.com/page",
                "url2": "http://example.com/otherpage", "notes": "",
                "id": stage.id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertTemplateUsed(response, "error.html")

    def test_delete_stage(self):
        """ Tests that delete_stage method properly deletes a stage when authorized"""
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_stages + 1, Stage.objects.count())
        t_id = stage.id
        response = self.client.get(reverse("delete_stage", args=(t_id,)))
        second_num_stages = Stage.objects.count()
        #TODO: self.assertEqual(response.status_code, 200)
        self.assertEqual(first_num_stages, second_num_stages)

    def test_delete_stage_unauthorized(self):
        """ Tests that delete_stage method raises error when unauthorized"""
        self.set_roles([])
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        t_id = stage.id
        self.client.get(reverse("delete_stage", args=(t_id,)))
        second_num_stages = Stage.objects.count()
        self.assertNotEqual(first_num_stages, second_num_stages)

    def test_delete_stage_nonexistent(self):
        """ Tests that delete_stage method raises error for non-existent Stage"""
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        t_id = NONEXISTANT_STAGE_ID
        #self.client.get(reverse("delete_stage", args=(t_id,)))
        second_num_stages = Stage.objects.count()
        self.assertRaisesSpecific(MISSING_STAGE, delete_stage, self.request, (t_id,))
        self.assertNotEqual(first_num_stages, second_num_stages)

    def test_delete_stage_wrong_course(self):
        """ Tests that delete_stage method raises error for existent Stage but for
            wrong course"""
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_OTHER_COURSE_ID)
        t_id = stage.id
        #self.client.get(reverse("delete_stage", args=(t_id,)))
        second_num_stages = Stage.objects.count()
        self.assertRaisesSpecific(MISSING_STAGE, delete_stage, self.request, (t_id,))
        self.assertNotEqual(first_num_stages, second_num_stages)
