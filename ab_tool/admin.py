from django.contrib import admin

from ab_tool.models import (CourseSettings, CourseStudent, InterventionPoint,
    InterventionPointUrl, Track)

admin.site.register(CourseSettings)
admin.site.register(CourseStudent)
admin.site.register(InterventionPoint)
admin.site.register(InterventionPointUrl)
admin.site.register(Track)
