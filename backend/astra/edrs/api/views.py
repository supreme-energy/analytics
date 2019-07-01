from django.db.models import Case, Value, When, FloatField, F, ExpressionWrapper
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from edrs.models import (EDRRaw, EDRProcessed,
                         EDRDrilled, EDRCXN, EDRComment, EDRTrip)
from edrs.api.serializers import (EDRRawSerializer, EDRProcessedSerializer,
                                  EDRDrilledSerializer, EDRCXNSerializer, EDRTripSerializer,
                                  EDRCommentSerializer, RTAVerticalSerializer, RTACurveSerializer,WellOverviewSerializer)
from jobs.models import WellConnector


class EDRRawViewSet(viewsets.ModelViewSet):
    serializer_class = EDRRawSerializer
    queryset = EDRRaw.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class EDRProcessedViewSet(viewsets.ModelViewSet):
    serializer_class = EDRProcessedSerializer
    queryset = EDRProcessed.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class RTAVerticalViewSet(viewsets.ModelViewSet):
    serializer_class = RTAVerticalSerializer
    queryset = WellConnector.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class RTACurveViewSet(viewsets.ModelViewSet):
    serializer_class = RTACurveSerializer
    queryset = WellConnector.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class EDRDrilledViewSet(viewsets.ModelViewSet):
    serializer_class = EDRDrilledSerializer
    queryset = EDRDrilled.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class EDRCXNViewSet(viewsets.ModelViewSet):
    serializer_class = EDRCXNSerializer
    queryset = EDRCXN.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class EDRTripViewSet(viewsets.ModelViewSet):
    serializer_class = EDRTripSerializer
    queryset = EDRTrip.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class EDRCommentViewSet(viewsets.ModelViewSet):
    serializer_class = EDRCommentSerializer
    queryset = EDRComment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class WellOverviewViewSet(viewsets.ModelViewSet):
    serializer_class = WellOverviewSerializer
    queryset = WellConnector.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'