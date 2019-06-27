from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from projections.models import Projection
from .serializers import ProjectionSerializer


class ProjectionViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectionSerializer
    queryset = Projection.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'
