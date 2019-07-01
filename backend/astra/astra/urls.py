from django.contrib import admin
from django.urls import path, include
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('api/bhas/', include('bhas.api.urls.bhas')),
    path('api/edrcomments/', include('edrs.api.urls.edrcomments')),
    path('api/edrcxn/', include('edrs.api.urls.edrcxn')),
    path('api/edrdrilled/', include('edrs.api.urls.edrdrilled')),
    path('api/edrprocessed/', include('edrs.api.urls.edrprocessed')),
    path('api/edrraw/', include('edrs.api.urls.edrraw')),
    path('api/edrtrip/', include('edrs.api.urls.edrtrip')),
    path('api/formations/', include('jobs.api.urls.formations')),
    path('api/intervals/', include('jobs.api.urls.intervals')),
    path('api/jobs/', include('jobs.api.urls.jobs')),
    path('api/personnel/', include('personnel.api.urls.personnel')),
    path('api/plans/', include('plans.api.urls.plans')),
    path('api/projections/', include('projections.api.urls')),
    path('api/rta-curves/', include('edrs.api.urls.rta-curves')),
    path('api/rta-verticals/', include('edrs.api.urls.rta-verticals')),
    path('api/surveys/', include('surveys.api.urls.surveys')),
    path('api/users/', include('personnel.api.urls.users')),
    path('api/well-connectors/', include('jobs.api.urls.well-connectors')),
    path('api/welloverview/', include('edrs.api.urls.welloverview')),
    path('docs/', include_docs_urls(title='Astra_Analytics'))
]
