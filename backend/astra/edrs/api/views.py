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
    
    def get_queryset(self):
        query_params = self.request.query_params
        job = query_params.get('job', None)
        hole_depth_gte = query_params.get('hole_depth_gte', None)
        hole_depth_lte = query_params.get('hole_depth_lte', None)
        rig_time_gte = query_params.get('rig_time_gte', None)
        rig_time_lte = query_params.get('rig_time_lte', None)
        creation_date = query_params.get('creation_date', None)
        uid = query_params.get('uid', None)
        edr_raw = query_params.get('edr_raw', None)
        interval = query_params.get('interval', None)
        bha = query_params.get('bha', None)
        formation = query_params.get('formation', None)
        drilled_ft = query_params.get('drilled_ft', None)
        bit_rpm = query_params.get('bit_rpm', None)
        slide_status = query_params.get('slide_status', None)
        rot_status = query_params.get('rot_status', None)
        normalized_tf = query_params.get('normalized_tf', None)
        slide_count = query_params.get('slide_count', None)
        rot_count = query_params.get('rot_count', None)
        stand_count = query_params.get('stand_count', None)
        astra_mse = query_params.get('astra_mse', None)
        slide_value_tf = query_params.get('slide_value_tf', None)
        rop_i = query_params.get('rop_i', None)
        rop_a = query_params.get('rop_a', None)

        if (job or hole_depth_gte or hole_depth_lte or rig_time_gte or rig_time_lte or creation_date or uid or edr_raw or interval or bha or 
            formation or drilled_ft or bit_rpm or slide_status or rot_status or normalized_tf or slide_count or rot_count or stand_count or 
            astra_mse or slide_value_tf or rop_i or rop_a):
            
            queryset_list = EDRDrilled.objects.all()
            if job:
                queryset_list = queryset_list.filter(edr_raw__job=job)
            if hole_depth_gte:
                queryset_list = queryset_list.filter(edr_raw__hole_depth__gte=hole_depth_gte)
            if hole_depth_lte:
                queryset_list = queryset_list.filter(edr_raw__hole_depth__lte=hole_depth_lte)
            if rig_time_gte:
                queryset_list = queryset_list.filter(edr_raw__rig_time__gte=rig_time_gte)
            if rig_time_lte:
                queryset_list = queryset_list.filter(edr_raw__rig_time__lte=rig_time_lte)
            if creation_date:
                queryset_list = queryset_list.filter(creation_date=creation_date)
            if uid:
                queryset_list = queryset_list.filter(uid=uid)
            if edr_raw:
                queryset_list = queryset_list.filter(edr_raw=edr_raw)
            if interval:
                queryset_list = queryset_list.filter(interval=interval)
            if bha:
                queryset_list = queryset_list.filter(bha=bha)
            if formation:
                queryset_list = queryset_list.filter(formation=formation)
            if drilled_ft:
                queryset_list = queryset_list.filter(drilled_ft=drilled_ft)
            if bit_rpm:
                queryset_list = queryset_list.filter(bit_rpm=bit_rpm)
            if slide_status:
                queryset_list = queryset_list.filter(slide_status=slide_status)
            if rot_status:
                queryset_list = queryset_list.filter(rot_status=rot_status)
            if normalized_tf:
                queryset_list = queryset_list.filter(normalized_tf=normalized_tf)
            if slide_count:
                queryset_list = queryset_list.filter(slide_count=slide_count)
            if rot_count:
                queryset_list = queryset_list.filter(rot_count=rot_count)
            if stand_count:
                queryset_list = queryset_list.filter(stand_count=stand_count)
            if astra_mse:
                queryset_list = queryset_list.filter(astra_mse=astra_mse)
            if slide_value_tf:
                queryset_list = queryset_list.filter(slide_value_tf=slide_value_tf)
            if rop_i:
                queryset_list = queryset_list.filter(rop_i=rop_i)
            if rop_a:
                queryset_list = queryset_list.filter(rop_a=rop_a)
            return queryset_list
        else:
            return EDRDrilled.objects.all()






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