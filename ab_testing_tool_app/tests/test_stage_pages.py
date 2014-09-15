from django.core.urlresolvers import reverse
from mock import patch

from ab_testing_tool_app.constants import STAGE_URL_TAG
from ab_testing_tool_app.models import (Stage, StageUrl, Track)
from ab_testing_tool_app.tests.common import (SessionTestCase, TEST_COURSE_ID,
    TEST_OTHER_COURSE_ID, NONEXISTENT_STAGE_ID, APIReturn, LIST_MODULES,
    TEST_STUDENT_ID)
from ab_testing_tool_app.exceptions import (NO_URL_FOR_TRACK,
    COURSE_TRACKS_NOT_FINALIZED, MISSING_STAGE, UNAUTHORIZED_ACCESS,
    DELETING_INSTALLED_STAGE, NO_TRACKS_FOR_COURSE)


class TestStagePages(SessionTestCase):
    """ Tests related to Stages and Stage-related pages and methods """
    def test_deploy_stage_admin(self):
        """ Tests deploy stage for admins redirects to edit stage """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)))
        self.assertRedirects(response, reverse("edit_stage", args=(stage.id,)))
    
    def test_create_stage_view(self):
        """ Tests edit_stage template renders for url 'create_stage' when authenticated """
        response = self.client.get(reverse("create_stage"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
    
    def test_create_stage_view_unauthorized(self):
        """ Tests edit_stage template does not render for url 'create_stage' when unauthorized """
        self.set_roles([])
        response = self.client.get(reverse("create_stage"), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view(self):
        """ Tests edit_stage template renders when authenticated """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("edit_stage", args=(stage.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
    
    def test_edit_stage_view_unauthorized(self):
        """ Tests edit_stage template renders when unauthorized """
        self.set_roles([])
        stage = Stage.objects.create(name="stage1")
        t_id = stage.id
        response = self.client.get(reverse("edit_stage", args=(t_id,)), follow=True)
        self.assertTemplateNotUsed(response, "edit_stage.html")
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_create_stage_unauthorized(self):
        """ Tests that create_stage unauthorized """
        self.set_roles([])
        num_stages = Stage.objects.count()
        num_stageurls = StageUrl.objects.count()
        data = {"name": "stage",
                STAGE_URL_TAG + "1": "http://example.com/page",
                STAGE_URL_TAG + "2": "http://example.com/otherpage",
                "notes": "hi"}
        response = self.client.post(reverse("submit_create_stage"), data,
                                    follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(num_stages, Stage.objects.count())
        self.assertEqual(num_stageurls, StageUrl.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_edit_stage_view_with_stageurls(self):
        """ Tests edit_stage template renders with StageUrls """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1", course_id=TEST_COURSE_ID)
        track2 = Track.objects.create(name="track2", course_id=TEST_COURSE_ID)
        stageurl = StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        response = self.client.get(reverse("edit_stage", args=(stage.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_stage.html")
        self.assertIn("tracks", response.context)
        self.assertEqual(set(response.context["tracks"]), set([(track,stageurl), (track2,None)]))
    
    def test_submit_edit_stage_unauthorized(self):
        """ Tests that submit_edit_stage when unauthorized """
        self.set_roles([])
        stage = Stage.objects.create(name="old_name",
                                             course_id=TEST_COURSE_ID)
        stage_id = stage.id
        num_stages = Stage.objects.count()
        data = {"name": "new_name",
                "notes": "new notes",
                "id": stage_id}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertEqual(num_stages, Stage.objects.count())
        self.assertTemplateUsed(response, "not_authorized.html")
    
    def test_submit_edit_stage_nonexistent(self):
        """ Tests that submit_edit_stage method raises error for non-existent Stage """
        data = {"name": "new_name",
                "notes": "hi",
                "id": NONEXISTENT_STAGE_ID}
        response = self.client.post(reverse("submit_edit_stage"), data,
                                    follow=True)
        self.assertError(response, MISSING_STAGE)
    
    def test_deploy_stage_view(self):
        """ Tests deploy stage  """
        stage = Stage.objects.create(name="stage1", course_id=TEST_COURSE_ID)
        track = Track.objects.create(name="track1")
        StageUrl.objects.create(stage=stage, url="http://www.example.com", track=track)
        response = self.client.get(reverse("deploy_stage", args=(stage.id,)),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_stage_unauthorized(self):
        """ Tests that delete_stage method raises error when unauthorized """
        self.set_roles([])
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        response = self.client.get(reverse("delete_stage", args=(stage.id,)),
                                   follow=True)
        second_num_stages = Stage.objects.count()
        self.assertTemplateUsed(response, "not_authorized.html")
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    def test_delete_stage_nonexistent(self):
        """ Tests that delete_stage method raises error for non-existent Stage """
        first_num_stages = Stage.objects.count()
        Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        stage_id = NONEXISTENT_STAGE_ID
        response = self.client.get(reverse("delete_stage", args=(stage_id,)),
                                   follow=True)
        second_num_stages = Stage.objects.count()
        self.assertError(response, MISSING_STAGE)
        self.assertNotEqual(first_num_stages, second_num_stages)
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_delete_stage_installed(self, _mock1):
        """ Tests that delete_stage method when stage is installed """
        first_num_stages = Stage.objects.count()
        stage = Stage.objects.create(name="testname", course_id=TEST_COURSE_ID)
        self.assertEqual(first_num_stages + 1, Stage.objects.count())
        ret_val = [True]
        with patch("ab_testing_tool_app.views.stage_pages.stage_is_installed",
                   return_value=ret_val):
            response = self.client.get(reverse("delete_stage", args=(stage.id,)),
                                       follow=True)
            second_num_stages = Stage.objects.count()
            self.assertNotEqual(first_num_stages, second_num_stages)
            self.assertError(response, DELETING_INSTALLED_STAGE)
