import csv
from django.http.response import HttpResponse

from ab_tool.models import ExperimentStudent, InterventionPointDeployments

def log_intervention_point_deployment(course_id, student, intervention_point):
    InterventionPointDeployments.objects.create(
            course_id=course_id, student=student,
            intervention_point=intervention_point
    )


def get_student_list_csv(course_id, file_title):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = ("attachment; filename=%s" % file_title)
    writer = csv.writer(response)
    # Write headers to CSV file
    headers = ["Student ID", "LIS Person Sourcedid", "Experiment", "Assigned Track",
               "Timestamp Last Updated"]
    writer.writerow(headers)
    # Write data to CSV file
    for s in ExperimentStudent.objects.filter(course_id=course_id):
        row = [s.student_id, s.lis_person_sourcedid, s.experiment.name,
               s.track.name, s.updated_on]
        writer.writerow(row)
    return response
