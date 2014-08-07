from django.conf.urls import patterns, include, url

from django.contrib import admin
from ab_testing_tool.views import render_treatment_control_panel, not_authorized, \
                deploy_treatment, new_treatment, create_treatment, \
                update_treatment, edit_treatment

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', render_treatment_control_panel, name='index'),
    url(r'^not_authorized$', not_authorized, name='not_authorized'),
    url(r'^create_treatment$', create_treatment, name='create_treatment'),
    url(r'^new_treatment$', new_treatment, name='new_treatment'),
    url(r'^update_treatment$', update_treatment, name='update_treatment'),
    url(r'^edit_treatment/(?P<t_id>\d+)$', edit_treatment, name='edit_treatment'),
    url(r'^treatment/(?P<t_id>\d+)$', deploy_treatment, name='render_treatment'),
    # Examples:
    # url(r'^$', 'project_name.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
)
