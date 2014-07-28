from django.conf.urls import patterns, include, url

from django.contrib import admin
from ab_testing_tool.views import index
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', index)
    # Examples:
    # url(r'^$', 'project_name.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # url(r'^admin/', include(admin.site.urls)),
)
