from django.conf.urls import patterns, include, url
from easycare.settings import MEDIA_ROOT
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from frontend.views import * #PatientReisterCreateView, HistoryListView, RecordDetailView, RecordPendingListView, RecordResponseView, RecordDeleteView
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT }),
        url(r'^$', 'frontend.views.homepage'),
        url(r'^homepage/', 'frontend.views.homepage', name='homepage'),
        url(r'^aboutus/', 'frontend.views.aboutus', name='about-us'),
        url(r'^contactus/', 'frontend.views.contactus', name='contact-us'),
        url(r'^accounts/login/$', login , name='login'),
        url(r'^accounts/logout/$', logout, {'next_page':'/homepage/'}, name='logout'),
        url(r'^records/create/$', 'frontend.views.record_create', name="record-create"),
        url(r'^records/pending/$', login_required(RecordPendingListView.as_view()), name="record-pending"),
        url(r'^records/history/$', login_required(HistoryListView.as_view()), name="record-history"),
        url(r'^records/(?P<pk>\d+)/detail/$', login_required(RecordDetailView.as_view()), name="record-detail"),
        url(r'^records/(?P<record>\d+)/delete/$', login_required(RecordDeleteView.as_view()), name="record-delete"),
        url(r'^records/(?P<record>\d+)/reply/$', login_required(RecordResponseView.as_view()), name="record-reply"),
        url(r'^records/(?P<record_id>\d+)/graph/weight/$', 'frontend.views.graph_weight', name="record-graph-weight"),
        url(r'^records/(?P<record_id>\d+)/graph/drug/$', 'frontend.views.graph_drug', name="record-graph-drug"),
        url(r'^records/(?P<record_id>\d+)/graph/pressure/$', 'frontend.views.graph_pressure', name="record-graph-amount"),
        url(r'^patients/register/$', login_required(PatientReisterCreateView.as_view()), name="patient-register"),
        url(r'^patients/$', login_required(PatientListView.as_view()), name="patient"),
        url(r'^patients/(?P<pk>\d+)/$', login_required(PatientUpdateView.as_view()), name="patient-update"),
)
