from mock import MagicMock

from ab_tool.controllers import (intervention_point_url,
    format_url, post_param, format_weighting,
    assign_track_and_create_student)
from ab_tool.tests.common import (SessionTestCase, TEST_STUDENT_ID)
from ab_tool.exceptions import (BAD_STAGE_ID, INPUT_NOT_ALLOWED,
    CSV_UPLOAD_NEEDED, NO_TRACKS_FOR_EXPERIMENT, TRACK_WEIGHTS_NOT_SET)
from ab_tool.models import Experiment, ExperimentStudent


class TestControllers(SessionTestCase):
    def test_assign_track_and_create_student_creates_student(self):
        """ Tests function assign_track_and_create_student creates student object
            via DB count """
        experiment = self.create_test_experiment(assignment_method=Experiment.UNIFORM_RANDOM)
        self.create_test_track(experiment=experiment)
        student_count = ExperimentStudent.objects.count()
        student = assign_track_and_create_student(experiment, TEST_STUDENT_ID, TEST_STUDENT_ID)
        self.assertTrue(ExperimentStudent.objects.count() == student_count + 1 )
        self.assertTrue(student in ExperimentStudent.objects.all())
    
    def test_assign_track_and_create_student_with_weights(self):
        experiment = self.create_test_experiment(assignment_method=Experiment.WEIGHTED_PROBABILITY_RANDOM)
        track = self.create_test_track(experiment=experiment)
        self.create_test_track_weight(track=track, experiment=experiment)
        student_count = ExperimentStudent.objects.count()
        student = assign_track_and_create_student(experiment, TEST_STUDENT_ID, TEST_STUDENT_ID)
        self.assertTrue(ExperimentStudent.objects.count() == student_count + 1 )
        self.assertTrue(student in ExperimentStudent.objects.all())
        self.assertTrue(student.track == track)

    def test_assign_track_and_create_student_without_weights_raises_error(self):
        experiment = self.create_test_experiment(assignment_method=Experiment.WEIGHTED_PROBABILITY_RANDOM)
        self.create_test_track(experiment=experiment)
        data = {"experiment": experiment, "student_id":TEST_STUDENT_ID,
                "lis_person_sourcedid": TEST_STUDENT_ID}
        self.assertRaisesSpecific(TRACK_WEIGHTS_NOT_SET, assign_track_and_create_student, **data)
    
    def test_assign_track_and_create_student_raises_error_for_no_tracks(self):
        experiment = self.create_test_experiment()
        data = {"experiment": experiment, "student_id":TEST_STUDENT_ID,
                "lis_person_sourcedid": TEST_STUDENT_ID}
        self.assertRaisesSpecific(NO_TRACKS_FOR_EXPERIMENT, assign_track_and_create_student, **data)
    
    def test_assign_track_and_create_student_raises_error_for_no_csv(self):
        experiment = self.create_test_experiment(assignment_method=Experiment.CSV_UPLOAD)
        data = {"experiment": experiment, "student_id":TEST_STUDENT_ID,
                "lis_person_sourcedid": TEST_STUDENT_ID}
        self.assertRaisesSpecific(CSV_UPLOAD_NEEDED, assign_track_and_create_student, **data)
    
    def test_format_weighting(self):
        self.assertTrue(1 == format_weighting("1"))
        self.assertTrue(100 == format_weighting("100"))
    
    def test_format_weighting_raises_error(self):
        self.assertRaisesSpecific(INPUT_NOT_ALLOWED, format_weighting, "-1")
        self.assertRaisesSpecific(INPUT_NOT_ALLOWED, format_weighting, "1001")
    
    def test_intervention_point_url_contains_intervention_point_id(self):
        """ Tests that intervention_point_url contains the string of the intervention_point_id """
        intervention_point_id = 999888777
        url = intervention_point_url(self.request, intervention_point_id)
        self.assertIn(str(intervention_point_id), url)
    
    def test_intervention_point_url_works_with_string_id(self):
        """ Tests that intervention_point_url succeeds when intervention_point_id is a number string """
        intervention_point_id = "999888777"
        url = intervention_point_url(self.request, intervention_point_id)
        self.assertIn(intervention_point_id, url)
    
    def test_intervention_point_url_contains_host(self):
        """ Tests that intervention_point_url's output contains the host of the request """
        intervention_point_id = "1"
        url = intervention_point_url(self.request, intervention_point_id)
        self.assertIn(self.request.get_host(), url)
    
    def test_intervention_point_url_errors(self):
        """ Tests that intervention_point_url errors when passed a non-numeral intervention_point_id """
        self.assertRaisesSpecific(BAD_STAGE_ID, intervention_point_url, self.request, None)
        self.assertRaisesSpecific(BAD_STAGE_ID, intervention_point_url, self.request, "str")
    
    def test_format_url_passthrough(self):
        """ Tests that format_url doesn't change a proper http:// url """
        url = "http://example.com/http_stuff?thing=other_thing"
        self.assertEqual(url, format_url(url))
    
    def test_format_url_https_passthrough(self):
        """ Tests that format_url doesn't change a proper https:// url """
        url = "https://example.com/http_stuff?thing=other_thing"
        self.assertEqual(url, format_url(url))
    
    def test_format_url_adds_http(self):
        """ Tests that format_url adds http:// to a url missing it """
        url = "www.example.com/http_stuff?thing=other_thing"
        self.assertEqual("http://" + url, format_url(url))
    
    def test_post_param_success(self):
        """ Test that post_param returns correct value when param is present """
        request = MagicMock()
        request.POST = {"param_name": "param_value"}
        self.assertEqual(post_param(request, "param_name"), "param_value")
    
    def test_post_param_error(self):
        """ Test that post_param errors when requested param is missing """
        request = MagicMock()
        request.POST = {}
        self.assertRaises(Exception, post_param, request, "param_name")
