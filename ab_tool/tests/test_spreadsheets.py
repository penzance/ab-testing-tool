
from ab_tool.spreadsheets import (get_student_list_csv, get_intervention_point_interactions_csv,
                                  get_track_selection_xlsx, get_track_selection_csv,
                                  parse_uploaded_file, parse_row)
from ab_tool.models import (InterventionPointUrl, ExperimentStudent, Experiment,
                            InterventionPointInteraction)

from ab_tool.tests.common import (SessionTestCase, TEST_COURSE_ID, TEST_STUDENT_ID)

from django.test import RequestFactory
from mock import patch, MagicMock, ANY, Mock
from error_middleware.exceptions import Renderable404

'''
Setup some test data
'''
TEST_XLS_FILE_NAME = 'test.xls'
TEST_XLSX_FILE_NAME = 'test.xlsx'
TEST_CSV_FILE_NAME = 'test.csv'
TEST_DOMAIN = 'http://www.example.com'
TEST_STUDENT_EMAIL = 'StudentB@example.com'
TEST_STUDENT_DICT = {'10123478': 'StudentA',
                     '20123278': 'StudentB',
                     '34512278': 'StudentC',
                     '40212478': 'StudentD',
                     }
TEST_CONTENT_TYPE = [('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                     ('Content-Disposition', 'attachment; filename=test.xlsx')]

TEST_TRACK_SELECTION_RESPONSE = ['Student Name,Student ID,Experiment,Assigned Track\r\n',
                                 'StudentD,40212478,Experiment 1,\r\n',
                                 'StudentB,20123278,Experiment 1,\r\n',
                                 'StudentA,10123478,Experiment 1,\r\n',
                                 'StudentC,34512278,Experiment 1,\r\n']

TEST_ROW = [TEST_STUDENT_DICT['20123278'],'20123278','Experiment 1', 'track1']

TEST_ROW_NUMBER = 1

class TestSpreadsheets(SessionTestCase):

    def setUp(self):

        self.request = RequestFactory().get('/fake-path')
        self.request.user = Mock(name='user_mock')
        self.request.session = { 'oauth_return_uri': TEST_DOMAIN,
                                 'LTI_LAUNCH': {
                                     'custom_canvas_api_domain': TEST_DOMAIN,
                                     'lis_person_contact_email_primary': TEST_STUDENT_EMAIL,
                                     'custom_canvas_course_id': TEST_COURSE_ID,
                                     },
                                }

        self.experiment = Experiment.get_placeholder_course_experiment(TEST_COURSE_ID)
        self.experiment.update(tracks_finalized=True)
        self.intervention_point = self.create_test_intervention_point(name='intervention_point1',
                                                                      experiment=self.experiment)
        self.track1 = self.create_test_track(name='track1',
                                             experiment=self.experiment)

        self.intervention_point2 = self.create_test_intervention_point(name='intervention_point2',
                                                                       experiment=self.experiment)
        self.track2 = self.create_test_track(name='track2',
                                             experiment=self.experiment)

        self.student = ExperimentStudent.objects.create(course_id=TEST_COURSE_ID,
                                                        experiment=self.experiment,
                                                        student_id=TEST_STUDENT_ID,
                                                        track=self.track1)

        InterventionPointUrl.objects.create(intervention_point=self.intervention_point,
                                            track=self.track1,
                                            url=TEST_DOMAIN)

        InterventionPointUrl.objects.create(intervention_point=self.intervention_point2,
                                            track=self.track2,
                                            url='http://www.incorrect-domain.com')

        InterventionPointInteraction.objects.create(course_id=TEST_COURSE_ID,
                                                    student=self.student,
                                                    intervention_point=self.intervention_point,
                                                    experiment=self.experiment,
                                                    track=self.track1,
                                                    url=TEST_DOMAIN)


    def test_get_student_list_csv(self):
        """
        Test that get_student_list_csv returns the correct data from the supplied experiment.
        """
        response = get_student_list_csv(self.experiment, TEST_XLSX_FILE_NAME)
        streaming_list = list(response.streaming_content)
        self.assertTrue(TEST_STUDENT_ID in streaming_list[1])
        self.assertTrue('Experiment 1' in streaming_list[1])
        self.assertTrue('track1'in streaming_list[1])

    def test_get_intervention_point_interactions_csv(self):
        """
        Test that get_intervention_point_interactions_csv returned the correct data
        from the supplied experiment
        """
        response = get_intervention_point_interactions_csv(self.experiment, TEST_XLSX_FILE_NAME)
        streaming_list = list(response.streaming_content)
        self.assertTrue(TEST_STUDENT_ID in streaming_list[1])
        self.assertTrue('Experiment 1' in streaming_list[1])
        self.assertTrue(TEST_DOMAIN in streaming_list[1])

    @patch('ab_tool.spreadsheets.get_unassigned_students')
    def test_get_track_selection_xlsx(self, mock_get_unassigned_students):
        """
        Test that get_track_selection_xlsx returns the correct content type and file name.
        """
        mock_get_unassigned_students.return_value = TEST_STUDENT_DICT
        response = get_track_selection_xlsx(self.request, self.experiment)
        self.assertEqual(response.items(), TEST_CONTENT_TYPE)

    @patch('ab_tool.spreadsheets.get_unassigned_students')
    def test_get_track_selection_csv(self, mock_get_unassigned_students):
        """
        Test that get_track_selection_csv returns the correct data. In this case
        the streaming list is the data that would be downloaded into a csv file.
        """
        mock_get_unassigned_students.return_value = TEST_STUDENT_DICT
        response = get_track_selection_csv(self.request, self.experiment)
        streaming_list = list(response.streaming_content)
        self.assertEqual(streaming_list, TEST_TRACK_SELECTION_RESPONSE)

    @patch('ab_tool.spreadsheets.xlrd.open_workbook')
    def test_parse_uploaded_xlsx_file(self, mock_open_workbook):
        """
        Test that parse_uploaded_xlsx_file calls the xlrd.open_workbook method with the
        appropriate data for files of type xlsx
        """
        result = parse_uploaded_file(self.experiment, TEST_STUDENT_DICT, TEST_TRACK_SELECTION_RESPONSE, TEST_XLSX_FILE_NAME)
        mock_open_workbook.assert_called_with(file_contents=TEST_TRACK_SELECTION_RESPONSE)

    @patch('ab_tool.spreadsheets.xlrd.open_workbook')
    def test_parse_uploaded_xls_file(self, mock_open_workbook):
        """
        Test that parse_uploaded_xlsx_file calls the xlrd.open_workbook method with the
        appropriate data for files of type xls
        """
        result = parse_uploaded_file(self.experiment, TEST_STUDENT_DICT, TEST_TRACK_SELECTION_RESPONSE, TEST_XLS_FILE_NAME)
        mock_open_workbook.assert_called_with(file_contents=TEST_TRACK_SELECTION_RESPONSE)

    @patch('ab_tool.spreadsheets.csv.reader')
    @patch('ab_tool.spreadsheets.parse_row')
    def test_parse_uploaded_csv_file(self, mock_parse_row, mock_csv_reader):
        """
        Test that parse_uploaded_csv_file calls the csv.reader method with the
        appropriate data for files of type csv
        """
        new_row = ','.join(TEST_ROW)
        mock_csv_reader.return_value = [new_row]
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        result = parse_uploaded_file(self.experiment, TEST_STUDENT_DICT,
                                     TEST_TRACK_SELECTION_RESPONSE[1],
                                     TEST_CSV_FILE_NAME)
        data = TEST_TRACK_SELECTION_RESPONSE[1].split('\n')[1:]
        mock_csv_reader.assert_called_with(data)
        mock_parse_row.assert_called_with(new_row, 2,
                                          self.experiment, tracks,
                                          TEST_STUDENT_DICT, {}, [])

    @patch('ab_tool.spreadsheets.xlrd.open_workbook')
    def test_parse_uploaded_file_invalid_file_name(self, mock_open_workbook):
        """
        Test that parse_uploaded_file raises a Renderable404 when a invalid file
        type is specified
        """
        self.assertRaises(Renderable404, parse_uploaded_file, self.experiment,
                          TEST_STUDENT_DICT, TEST_TRACK_SELECTION_RESPONSE, "test.xslx")


    def test_parse_row(self):
        """
        Test that parse_row populates the student dictionary with the correct
        values when the supplied data is correct
        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        parse_row(TEST_ROW, TEST_ROW_NUMBER, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(students.keys(), ['20123278'])

    def test_parse_row_missing_track(self):
        """
        Test that parse_row populates the errors list with the 'missing track name' error message
        when no track name is supplied
        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        # row with missing track
        row = [TEST_STUDENT_DICT['20123278'], '20123278', 'Experiment 1', ]
        parse_row(row, TEST_ROW_NUMBER, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: missing track name"])

    def test_parse_row_invalid_track_name(self):
        """
        Test that parse_row populates the errors list with the 'invalid track name' error message
        when the supplied track name does not match the tracks in the experiment
        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        # row with invalid track name
        row = [TEST_STUDENT_DICT['20123278'], '20123278', 'Experiment 1', 'track3']
        parse_row(row, TEST_ROW_NUMBER, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: invalid track name 'track3'"])

    def test_parse_row_wrong_experiment_name(self):
        """
        Test that parse_row populates the errors list with the 'wrong experiment name' error message
        when an invalid experiemnt name is supplied
        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        # row with invalid experiment name
        row = [TEST_STUDENT_DICT['20123278'], '20123278', 'Experiment 2', 'track2']
        parse_row(row, TEST_ROW_NUMBER, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: wrong experiment name 'Experiment 2'"])

    def test_parse_row_missing_row(self):
        """
        Test that parse_row returns None when row is None
        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        # missing row
        row = None
        result = parse_row(row, TEST_ROW_NUMBER, self.experiment, tracks,
                           TEST_STUDENT_DICT, students, errors)
        self.assertEqual(result, None)

    def test_parse_row_student_not_available_for_assignment(self):
        """
        Test that parse_row populates the errors list with the 'student x not available for assignment' error message
        when the student is not in the supplied list of valid students
        """
        students = {}
        errors = []
        tracks = {track.name: track for track in self.experiment.tracks.all()}
        # row with student who is able to be assigned
        row = ['StudentE', '50123278', 'Experiment 1', 'track2']
        parse_row(row, TEST_ROW_NUMBER, self.experiment, tracks, TEST_STUDENT_DICT, students, errors)
        self.assertEqual(errors, ["Row 1: student 'StudentE' not available for assignment"])

