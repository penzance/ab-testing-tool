from django.core.urlresolvers import reverse
from mock import patch

from ab_tool.controllers import intervention_point_url
from ab_tool.tests.common import (SessionTestCase, LIST_MODULES,
    LIST_ITEMS, APIReturn, TEST_COURSE_ID, TEST_OTHER_COURSE_ID)
from ab_tool.models import (ExperimentStudent, Experiment)
from ab_tool.views.main_pages import tool_config


class TestMainPages(SessionTestCase):
    """ Tests related to control panel and main pages """
    
    def test_not_authorized_renders(self):
        """ Tests that the not_authorized page renders """
        response = self.client.get(reverse("ab:not_authorized"), follow=True)
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_index_and_control_panel_view(self):
        """ Tests control_panel template renders when authenticated and with no
            contents returned from Canvas"""
        response = self.client.get(reverse("ab:index"), follow=True)
        self.assertOkay(response)
        self.assertTemplateUsed(response, "ab_tool/control_panel.html")
    
    @patch(LIST_MODULES, return_value=APIReturn([{"id": 0}]))
    def test_control_panel_with_module_and_item(self, _mock1):
        """ Tests control_panel template renders with items returned from Canvas"""
        mock_item = {"type": "ExternalTool",
                     "external_url": intervention_point_url(self.request, 0)}
        api_return = APIReturn([mock_item])
        with patch(LIST_ITEMS, return_value=api_return):
            response = self.client.get(reverse("ab:index"), follow=True)
            self.assertOkay(response)
            self.assertTemplateUsed(response, "ab_tool/control_panel.html")
    
    def test_unauthenticated_index(self):
        """ Tests control_panel template does not render when unauthorized"""
        self.set_roles([])
        response = self.client.get(reverse("ab:index"), follow=True)
        self.assertTemplateNotUsed(response, "ab_tool/control_panel.html")
        self.assertEqual(response.status_code, 401)
        self.assertTemplateUsed(response, "ab_tool/not_authorized.html")
    
    def test_index_context(self):
        """ Checks that the context of the index contains the relevant fields """
        response = self.client.get(reverse("ab:index"), follow=True)
        self.assertIn("intervention_points", response.context)
        self.assertIn("modules", response.context)
        self.assertIn("uninstalled_intervention_points", response.context)
        self.assertIn("experiments", response.context)
        self.assertIn("canvas_url", response.context)
    
    def test_index_context_experiments(self):
        """ Checks that the intervention_points and tracks passed to the index template
            contain values from the database """
        Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        intervention_point = self.create_test_intervention_point()
        response = self.client.get(reverse("ab:index"), follow=True)
        self.assertEqual(len(response.context["experiments"]), 1)
        self.assertSameIds([intervention_point], response.context["intervention_points"])
    
    def test_index_context_course_specific_intervention_points_and_experiments(self):
        """ Checks that the intervention_points and tracks passed to the index template
            only contain database values matching the course_id """
        intervention_point = self.create_test_intervention_point()
        self.create_test_intervention_point(course_id=TEST_OTHER_COURSE_ID)
        self.create_test_track()
        self.create_test_track(course_id=TEST_OTHER_COURSE_ID)
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        response = self.client.get(reverse("ab:index"), follow=True)
        self.assertSameIds([experiment], response.context["experiments"])
        self.assertSameIds([intervention_point], response.context["intervention_points"])
    
    def test_index_context_uninstalled_intervention_points(self):
        """ Tests that the context for the index correctly contains
            the uninstalled intervention_points for the course """
        intervention_point1 = self.create_test_intervention_point(name="intervention_point1")
        intervention_point2 = self.create_test_intervention_point(name="intervention_point2")
        with patch("ab_tool.views.main_pages.get_uninstalled_intervention_points",
                   return_value=[intervention_point1]):
            response = self.client.get(reverse("ab:index"), follow=True)
            self.assertSameIds(response.context["uninstalled_intervention_points"], [intervention_point1])
            self.assertSameIds(response.context["intervention_points"], [intervention_point1, intervention_point2])
    
    def test_index_context_modules(self):
        ret_val = [{"name": "module1"}]
        with patch("ab_tool.views.main_pages.get_modules_with_items",
                   return_value=ret_val):
            response = self.client.get(reverse("ab:index"), follow=True)
            self.assertEqual(response.context["modules"], ret_val)
    
    def test_tool_config(self):
        """ Tests that that tool_config page returns XML content"""
        response = self.client.get(reverse("ab:tool_config"))
        self.assertOkay(response)
        self.assertEqual(response._headers["content-type"],
                        ('Content-Type', 'text/xml'))
    
    def test_too_config_urls(self):
        """ Tests that urls for index and resource_selection appear in
            the return of tool config; this test doesn't use self.client
            in order to use the same request for building the comparison uris
            as it does for calling the view """
        index_url = self.request.build_absolute_uri(reverse("ab:index"))
        resource_selection_url = self.request.build_absolute_uri(
                reverse("ab:resource_selection"))
        response = tool_config(self.request)
        self.assertContains(response, index_url)
        self.assertContains(response, resource_selection_url)
    
    def test_download_data(self):
        """ Tests that download data returns a csv with a row for each student """
        track = self.create_test_track()
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, student_id=1,
                                         track=track, experiment=experiment)
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, student_id=2,
                                         track=track, experiment=experiment)
        response = self.client.get(reverse("ab:download_data", args=(experiment.id,)))
        self.assertEqual(response._headers["content-type"],
                         ('Content-Type', 'text/csv'))
        num_students = ExperimentStudent.objects.filter(course_id=TEST_COURSE_ID).count()
        # Add 2 to length for header and trailing newline
        self.assertEqual(len(response.content.split("\n")), num_students + 2)
    
    def test_download_data_course_specific(self):
        """ Tests that download data only uses student in the correct course """
        track = self.create_test_track()
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        ExperimentStudent.objects.create(course_id=TEST_COURSE_ID, student_id=1,
                                         track=track, experiment=experiment)
        ExperimentStudent.objects.create(course_id=TEST_OTHER_COURSE_ID, student_id=2,
                                         track=track, experiment=experiment)
        response = self.client.get(reverse("ab:download_data", args=(experiment.id,)))
        self.assertEqual(response._headers["content-type"],
                         ('Content-Type', 'text/csv'))
        num_students = ExperimentStudent.objects.filter(course_id=TEST_COURSE_ID).count()
        # Add 2 to length for header and trailing newline
        self.assertEqual(len(response.content.split("\n")), num_students + 2)
    
    def test_download_data_no_students(self):
        experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        response = self.client.get(reverse("ab:download_data", args=(experiment.id,)))
        self.assertEqual(response._headers["content-type"],
                         ('Content-Type', 'text/csv'))
        num_students = ExperimentStudent.objects.filter(course_id=TEST_COURSE_ID).count()
        self.assertEqual(num_students, 0)
        # Length is 2 for header and trailing newline
        self.assertEqual(len(response.content.split("\n")), 2)
