from django.db.models import Case, Value, When, FloatField, F, ExpressionWrapper
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from bhas.models import Bha
from .serializers import BhaSerializer


class BhaViewSet(viewsets.ModelViewSet):
    serializer_class = BhaSerializer
    queryset = Bha.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'
