from mock import MagicMock

from ab_tool.controllers import (intervention_point_url,
    validate_format_url, post_param, assign_track_and_create_student,
    validate_name, validate_weighting)
from ab_tool.tests.common import (SessionTestCase, TEST_STUDENT_ID, TEST_STUDENT_NAME)
from ab_tool.exceptions import (BAD_INTERVENTION_POINT_ID, CSV_UPLOAD_NEEDED,
    NO_TRACKS_FOR_EXPERIMENT, TRACK_WEIGHTS_NOT_SET,
    INVALID_URL_PARAM, MISSING_NAME_PARAM, PARAM_LENGTH_EXCEEDS_LIMIT,
    INCORRECT_WEIGHTING_PARAM)
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
                "student_name": TEST_STUDENT_NAME}
        self.assertRaisesSpecific(TRACK_WEIGHTS_NOT_SET, assign_track_and_create_student, **data)
    
    def test_assign_track_and_create_student_raises_error_for_no_tracks(self):
        experiment = self.create_test_experiment()
        data = {"experiment": experiment, "student_id":TEST_STUDENT_ID,
                "student_name": TEST_STUDENT_NAME}
        self.assertRaisesSpecific(NO_TRACKS_FOR_EXPERIMENT, assign_track_and_create_student, **data)
    
    def test_assign_track_and_create_student_raises_error_for_no_csv(self):
        experiment = self.create_test_experiment(assignment_method=Experiment.CSV_UPLOAD)
        data = {"experiment": experiment, "student_id":TEST_STUDENT_ID,
                "student_name": TEST_STUDENT_NAME}
        self.assertRaisesSpecific(CSV_UPLOAD_NEEDED, assign_track_and_create_student, **data)
    
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
        self.assertRaisesSpecific(BAD_INTERVENTION_POINT_ID, intervention_point_url, self.request, None)
        self.assertRaisesSpecific(BAD_INTERVENTION_POINT_ID, intervention_point_url, self.request, "str")
    
    def test_validate_format_url_passthrough(self):
        """ Tests that validate_format_url doesn't change a proper http:// url """
        url = "http://example.com/http_stuff?thing=other_thing"
        self.assertEqual(url, validate_format_url(url))
    
    def test_validate_format_url_https_passthrough(self):
        """ Tests that validate_format_url doesn't change a proper https:// url """
        url = "https://example.com/http_stuff?thing=other_thing"
        self.assertEqual(url, validate_format_url(url))
    
    def test_validate_format_url_adds_http(self):
        """ Tests that validate_format_url adds http:// to a url missing it """
        url = "www.example.com/http_stuff?thing=other_thing"
        self.assertEqual("http://" + url, validate_format_url(url))
    
    def test_validate_format_url_raises_error(self):
        """ Tests that validate_format_url adds http:// to a url missing it """
        url = "com"
        self.assertRaisesSpecific(INVALID_URL_PARAM, validate_format_url, url)
        url = "http://" + "a"*2046 + ".com"
        self.assertRaisesSpecific(INVALID_URL_PARAM, validate_format_url, url)
    
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
    
    def test_validate_name(self):
        """ Test validate_name validates properly """
        name = ""
        self.assertRaisesSpecific(MISSING_NAME_PARAM, validate_name, name)
        name = "a"*1000
        self.assertRaisesSpecific(PARAM_LENGTH_EXCEEDS_LIMIT, validate_name, name)
    
    def test_validate_weighting(self):
        """ Test validate_weighting validates properly """
        weighting =-1
        self.assertRaisesSpecific(INCORRECT_WEIGHTING_PARAM, validate_weighting, weighting)
        weighting = 101
        self.assertRaisesSpecific(INCORRECT_WEIGHTING_PARAM, validate_weighting, weighting)
