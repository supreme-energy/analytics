from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from functools import reduce
#from queryset_sequence import QuerySetSequence

from plans.models import Plan
from .serializers import PlanSerializer


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = PlanSerializer
    queryset = Plan.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'
