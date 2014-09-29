from django.contrib import admin

from ab_testing_tool_app.models import (CourseSettings, CourseStudent, InterventionPoint,
    InterventionPointUrl, Track)

admin.site.register(CourseSettings)
admin.site.register(CourseStudent)
admin.site.register(InterventionPoint)
admin.site.register(InterventionPointUrl)
admin.site.register(Track)
