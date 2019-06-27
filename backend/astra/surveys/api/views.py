from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from surveys.models import Survey
from .serializers import SurveySerializer


class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'
