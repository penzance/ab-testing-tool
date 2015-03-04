from ab_tool.models import InterventionPointInteraction

def log_intervention_point_interaction(course_id, student, intervention_point,
                                      experiment, track, intervention_point_url):
    InterventionPointInteraction.objects.create(
            course_id=course_id, student=student,
            intervention_point=intervention_point,
            experiment=experiment,
            track=track,
            url=intervention_point_url.url
    )

