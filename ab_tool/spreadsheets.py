import xlsxwriter
import StringIO
import xlrd
from django.http.response import HttpResponse

from ab_tool.models import (ExperimentStudent, InterventionPointInteraction)
from ab_tool.controllers import streamed_csv_response
from ab_tool.canvas import get_unsorted_students


def get_student_list_csv(experiment, file_title):
    def row_generator():
        yield ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track",
                   "Timestamp Last Updated"]
        for s in ExperimentStudent.objects.filter(experiment=experiment):
            yield [s.student_id, s.lis_person_sourcedid, s.experiment.name,
                   s.track.name, s.updated_on]
    return streamed_csv_response(row_generator(), file_title)


def get_intervention_point_interactions_csv(experiment, file_title):
    def row_generator():
        yield ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track",
                   "Intervention Point", "Intervention Point URL", "Timestamp Encountered"]
        for i in InterventionPointInteraction.objects.filter(experiment=experiment):
            yield [i.student.student_id, i.student.lis_person_sourcedid,
                   i.experiment.name, i.track.name,
                   i.intervention_point.name, i.url, i.created_on]
    return streamed_csv_response(row_generator(), file_title)


def get_track_selection_xlsx(request, experiment, file_title="test.xlsx"):
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 3, 20)
    headers = ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track"]
    worksheet.write_row(0, 0, headers)
    students = get_unsorted_students(request, experiment)
    # Row offsets of +1 below are to account for header
    for i, student in enumerate(students):
        row = [student["student_id"], student["lis_person_sourcedid"], experiment.name, ""]
        worksheet.write_row(i + 1, 0, row)
    # Add drop-down with track names as the only valid options for the missing column
    track_names = [t.name for t in experiment.tracks.all()]
    worksheet.data_validation(1, 3, len(students) + 1, 3,
                              {'validate': 'list', 'source': track_names,})
    workbook.close()
    output.seek(0)
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    response = HttpResponse(output.read(), content_type=content_type)
    response['Content-Disposition'] = ("attachment; filename=%s" % file_title)
    return response


def get_track_selection_csv(request, experiment, file_title="test.xlsx"):
    def row_generator():
        yield ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track"]
        # Write data to CSV file
        for s in get_unsorted_students(request, experiment):
            yield [s["student_id"], s["lis_person_sourcedid"], experiment.name, ""]
    return streamed_csv_response(row_generator(), file_title)


def parse_track_selection_xlsx(input_excel):
    workbook = xlrd.open_workbook(file_contents=input_excel.read())
    worksheet = workbook.sheet_by_index(0)
    # http://www.youlikeprogramming.com/2012/03/examples-reading-excel-xls-documents-using-pythons-xlrd/
