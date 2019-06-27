from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from localflavor.us.models import USStateField

from jobs.models import (Job, WellConnector, Interval, Formation)
from .serializers import (JobSerializer, IntervalSerializer,
                          WellConnectorSerializer, FormationSerializer)


class WellConnectorViewSet(viewsets.ModelViewSet):
    serializer_class = WellConnectorSerializer
    queryset = WellConnector.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class FormationViewSet(viewsets.ModelViewSet):
    serializer_class = FormationSerializer
    queryset = Formation.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class IntervalViewSet(viewsets.ModelViewSet):
    serializer_class = IntervalSerializer
    queryset = Interval.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'
