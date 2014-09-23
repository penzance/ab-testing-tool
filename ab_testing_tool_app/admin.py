from django.contrib import admin

from ab_testing_tool_app.models import (CourseSettings, CourseStudent, Stage,
    StageUrl, Track)

admin.site.register(CourseSettings)
admin.site.register(CourseStudent)
admin.site.register(Stage)
admin.site.register(StageUrl)
admin.site.register(Track)