from ab_tool.models import (ExperimentStudent, InterventionPointInteraction)
from ab_tool.controllers import streamed_csv_response


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

