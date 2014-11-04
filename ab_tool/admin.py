from django.contrib import admin

from ab_tool.models import (Experiment, ExperimentStudent, InterventionPoint,
    InterventionPointUrl, Track, InterventionPointDeployments)

admin.site.register(Experiment)
admin.site.register(ExperimentStudent)
admin.site.register(InterventionPoint)
admin.site.register(InterventionPointUrl)
admin.site.register(Track)
admin.site.register(InterventionPointDeployments)