from rest_framework import serializers, status
from bhas.models import Bha
from jobs.models import Job, Interval, Formation, WellConnector
from edrs.models import (EDRRaw, EDRProcessed,
                         EDRCXN, EDRComment, EDRTrip, EDRDrilled)
from surveys.models import Survey
import json
from django.db.models import Q, Avg, Max, Min, Sum, Count

class EDRRawSerializer(serializers.ModelSerializer):
    # job = serializers.SlugRelatedField(
    #     queryset=Job.objects.all(), slug_field='id')

    class Meta:
        model = EDRRaw
        fields = '__all__'
        read_only_field = ('id',)
        # extra_kwargs = {
        #     'svy_azi': {'allow_null': True, 'required': False},
        #     'svy_inc': {'allow_null': True, 'required': False},
        #     'tf_grav': {'allow_null': True, 'required': False},
        #     'tf_mag': {'allow_null': True, 'required': False},
        #     'total_spm': {'allow_null': True, 'required': False},
        #     'hookload': {'allow_null': True, 'required': False},
        #     'overpull': {'allow_null': True, 'required': False},
        #     'edr_mse': {'allow_null': True, 'required': False},
        #     'oscillator': {'allow_null': True, 'required': False},
        #     'edr_RS1': {'allow_null': True, 'required': False},
        #     'edr_RS2': {'allow_null': True, 'required': False},
        #     'edr_RS3': {'allow_null': True, 'required': False},
        #     'active': {'allow_null': True, 'required': False},
        #     'live_inc': {'allow_null': True, 'required': False},
        # }


class EDRProcessedSerializer(serializers.ModelSerializer):
    edr_raw = serializers.SlugRelatedField(
        queryset=EDRRaw.objects.all(), slug_field='id')

    class Meta:
        model = EDRProcessed
        fields = '__all__'
        read_only_field = ('id','bit_variance','data_gap','time_elapsed','tq_variance')



class EDRDrilledSerializer(serializers.ModelSerializer):
    interval = serializers.SlugRelatedField(
        queryset=Interval.objects.all(), slug_field='id')
    formation = serializers.SlugRelatedField(
        queryset=Formation.objects.all(), slug_field='id')
    bha = serializers.SlugRelatedField(
        queryset=Bha.objects.all(), slug_field='id')
    edr_raw = serializers.SlugRelatedField(
        queryset=EDRRaw.objects.all(), slug_field='id')

    class Meta:
        model = EDRDrilled
        fields = '__all__'
        read_only_field = ('id',)

class EDRDrilledParameterSerializer(serializers.ModelSerializer):
    rig_time = serializers.SerializerMethodField(read_only=True, required=False)
    hole_depth = serializers.SerializerMethodField(read_only=True, required=False)
    diff_pressure = serializers.SerializerMethodField(read_only=True, required=False)
    td_torque = serializers.SerializerMethodField(read_only=True, required=False)
    td_rpm = serializers.SerializerMethodField(read_only=True, required=False)
    connection_number = serializers.SerializerMethodField(read_only=True, required=False)

    def get_rig_time(self, obj):
        try: 
            return obj.edr_raw.rig_time
        except:
            return ""
    
    def get_hole_depth(self, obj):
        try: 
            return obj.edr_raw.hole_depth
        except:
            return ""
    def get_diff_pressure(self, obj):
        try: 
            return obj.edr_raw.diff_pressure
        except:
            return ""

    def get_td_torque(self, obj):
        try: 
            return obj.edr_raw.td_torque
        except:
            return ""

    def get_td_rpm(self, obj):
        try: 
            return obj.edr_raw.td_rpm
        except:
            return ""

    def get_connection_number(self, obj):
        try: 
            edr_process = EDRProcessed.objects.get(edr_raw=obj.edr_raw)
            return edr_process.cxn_count
        except:
            return ""


    class Meta:
        model = EDRDrilled
        fields = ('rig_time','hole_depth','rop_a', 'bit_rpm', 'astra_mse', 'slide_count', 'diff_pressure', 'td_torque', 'td_rpm', 'connection_number')
        read_only_field = ('id',)


class RTACurveSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')
    parameters = serializers.SerializerMethodField(read_only=True)

    def get_parameters(self, obj):
        drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid)

        # drilled_pks = drilled_on_uid.values_list('id', flat=True)
        drilled_slide_count = list(drilled_on_uid.values_list(
            'slide_count', flat=True))
        drilled_stand_count = list(drilled_on_uid.values_list(
            'stand_count', flat=True))
        drilled_normalized_tf = list(
            drilled_on_uid.values_list('normalized_tf', flat=True))
        drilled_slide_value_tf = list(drilled_on_uid.values_list(
            'slide_value_tf', flat=True))

        raw_hole_depth = list(drilled_on_uid.values_list(
            'edr_raw__hole_depth', flat=True))
        raw_rop_a = list(drilled_on_uid.values_list(
            'edr_raw__rop_a', flat=True))
        raw_rop_i = list(drilled_on_uid.values_list(
            'edr_raw__rop_i', flat=True))

        survey_on_uid = Survey.objects.filter(uid=obj.uid)

        survey_md = list(survey_on_uid.values_list('md', flat=True))
        survey_inc = list(survey_on_uid.values_list('inc', flat=True))
        survey_azi = list(survey_on_uid.values_list('azi', flat=True))
        survey_my = list(survey_on_uid.values_list('my', flat=True))
        survey_edr_dls = list(survey_on_uid.values_list('edr_dls', flat=True))
        survey_tvd = list(survey_on_uid.values_list('tvd', flat=True))
        survey_build_rate = list(
            survey_on_uid.values_list('build_rate', flat=True))
        survey_turn_rate = list(
            survey_on_uid.values_list('turn_rate', flat=True))

        parameters = {
            "slide_count": drilled_slide_count,
            "stand_count": drilled_stand_count,
            "normalized_tf": drilled_normalized_tf,
            "slide_value_tf": drilled_slide_value_tf,

            "hole_depth": raw_hole_depth,
            "rop_a": raw_rop_a,
            "rop_i": raw_rop_i,

            "md": survey_md,
            "inc": survey_inc,
            "azi": survey_azi,
            "my": survey_my,
            "dls": survey_edr_dls,
            "tvd": survey_tvd,
            "build_rate": survey_build_rate,
            "turn_rate": survey_turn_rate
        }

        return parameters

    class Meta:
        model = WellConnector
        fields = ('id', 'job', 'parameters', 'uid')
        read_only_field = ('id', 'job', 'parameters')


class RTAVerticalSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')
    parameters = serializers.SerializerMethodField(read_only=True)

    def get_parameters(self, obj):
        drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid)

        # drilled_pks = drilled_on_uid.values_list('id', flat=True)
        drilled_slide_count = list(drilled_on_uid.values_list(
            'slide_count', flat=True))
        drilled_stand_count = list(drilled_on_uid.values_list(
            'stand_count', flat=True))
        drilled_astra_mse = list(
            drilled_on_uid.values_list('astra_mse', flat=True))
        drilled_rot_count = list(drilled_on_uid.values_list(
            'rot_count', flat=True))

        # raw_drilled = EDRRaw.objects.filter(id__in=drilled_pks)

        raw_hole_depth = list(drilled_on_uid.values_list(
            'edr_raw__hole_depth', flat=True))
        raw_wob = list(drilled_on_uid.values_list('edr_raw__wob', flat=True))
        raw_td_rpm = list(drilled_on_uid.values_list(
            'edr_raw__td_rpm', flat=True))
        raw_flow_in = list(drilled_on_uid.values_list(
            'edr_raw__flow_in', flat=True))
        raw_rop_a = list(drilled_on_uid.values_list(
            'edr_raw__rop_a', flat=True))
        raw_rop_i = list(drilled_on_uid.values_list(
            'edr_raw__rop_i', flat=True))
        raw_diff_press = list(drilled_on_uid.values_list(
            'edr_raw__diff_press', flat=True))
        raw_pump_press = list(drilled_on_uid.values_list(
            'edr_raw__pump_press', flat=True))
        raw_td_torque = list(drilled_on_uid.values_list(
            'edr_raw__td_torque', flat=True))
        raw_flow_out = list(drilled_on_uid.values_list(
            'edr_raw__flow_out', flat=True))

        parameters = {
            "slide_count": drilled_slide_count,
            "stand_count": drilled_stand_count,
            "astra_mse": drilled_astra_mse,
            "rot_count": drilled_rot_count,

            "hole_depth": raw_hole_depth,
            "wob": raw_wob,
            "td_rpm": raw_td_rpm,
            "td_torque": raw_td_torque,
            "rop_a": raw_rop_a,
            "diff_press": raw_diff_press,
            "flow_in": raw_flow_in,
            "rop_i": raw_rop_i,
            "pump_press": raw_pump_press,
            "flow_out": raw_flow_out,
        }

        return parameters

    class Meta:
        model = WellConnector
        fields = ('id', 'job', 'parameters', 'uid')
        read_only_field = ('id', 'job', 'parameters')

class WellOverviewSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')
    #interval = serializers.SlugRelatedField(
        #queryset=Interval.objects.all(), slug_field='id')
    surface = serializers.SerializerMethodField(read_only=True)
    intermediate= serializers.SerializerMethodField(read_only=True)
    intermediate2 = serializers.SerializerMethodField(read_only=True)
    intermediate3 = serializers.SerializerMethodField(read_only=True)
    intermediate4 = serializers.SerializerMethodField(read_only=True)
    curve = serializers.SerializerMethodField(read_only=True)
    lateral = serializers.SerializerMethodField(read_only=True)
    tangent = serializers.SerializerMethodField(read_only=True)


    def get_surface(self, obj):

        s_interval_name=s_holesize=s_hole_depth_start=s_hole_depth_end =s_casingsize=0
        s_dt_start= s_dt_end =s_total_hours =s_drill_hours =s_svy_inc_start =s_svy_inc_end =s_rop_avg =0

        #sliding parameters
        s_sliding_footage=s_slide_pct_d=s_slide_pct_t=s_rop_avg_sliding=s_wob_avg_sliding=0
        s_top_drive_rpm_avg_sliding=s_bit_rpm_avg_sliding=s_flow_rate_avg_sliding=0
        s_diff_pressure_avg_sliding=s_pump_pressure_avg_sliding=s_top_drive_torque_avg_sliding=0

        #rotating parameters
        s_rotating_footage=s_rotate_pct_d=s_rotate_pct_t=s_rop_avg_rotating=s_wob_avg_rotating=0
        s_top_drive_rpm_avg_rotating=s_bit_rpm_avg_rotating=s_flow_rate_avg_rotating=0
        s_diff_pressure_avg_rotating=s_pump_pressure_avg_rotating=s_top_drive_torque_avg_rotating=0


        try:
            surface_on_uid = Interval.objects.get(name="Surface", job=obj.job)
        except:
            surface_on_uid = None
        
        if(surface_on_uid):
            s_interval_name = surface_on_uid.name
            s_holesize = surface_on_uid.hole_size
            s_casingsize = surface_on_uid.casing_size
            s_hole_depth_start = surface_on_uid.start_depth
            s_hole_depth_end = surface_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=s_hole_depth_start, edr_raw__hole_depth__lte=s_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=s_hole_depth_start, edr_raw__hole_depth__lte=s_hole_depth_end, slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=s_hole_depth_start, edr_raw__hole_depth__lte=s_hole_depth_end, slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            s_dt_start = drilled_aggregate.get('edr_raw__rig_time__min')
            s_dt_end  = drilled_aggregate.get('edr_raw__rig_time__max')
            s_total_hours = (s_dt_end-s_dt_start).total_seconds() / 3600
            s_drill_hours = len(drilled_on_uid) * obj.data_frequency / 3600
            s_rop_avg  = drilled_aggregate.get('rop_a__avg')
            
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))

            s_sliding_footage = sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum') > 0 else 0
            s_slide_pct_d = s_sliding_footage/(s_hole_depth_end-s_hole_depth_start) * 100
            s_slide_pct_t = len(slide_on_uid) * obj.data_frequency / 3600 / s_drill_hours
            s_rop_avg_sliding = sliding_aggregate.get('rop_a__avg')
            s_wob_avg_sliding = sliding_aggregate.get('edr_raw__wob__avg')
            s_top_drive_rpm_avg_sliding = sliding_aggregate.get('edr_raw__td_rpm__avg')
            s_bit_rpm_avg_sliding = sliding_aggregate.get('bit_rpm__avg')
            s_flow_rate_avg_sliding = sliding_aggregate.get('edr_raw__flow_in__avg')
            s_diff_pressure_avg_sliding = sliding_aggregate.get('edr_raw__diff_press__avg')
            s_pump_pressure_avg_sliding = sliding_aggregate.get('edr_raw__pump_press__avg')
            s_top_drive_torque_avg_sliding = sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            s_rotating_footage = s_hole_depth_end - s_hole_depth_start - s_sliding_footage
            s_rotate_pct_d = 100 - s_slide_pct_d
            s_rotate_pct_t = 100 - s_slide_pct_t
            s_rop_avg_rotating = rotating_aggregate.get('rop_a__avg')
            s_wob_avg_rotating = rotating_aggregate.get('edr_raw__wob__avg')
            s_top_drive_rpm_avg_rotating = rotating_aggregate.get('edr_raw__td_rpm__avg')
            s_bit_rpm_avg_rotating = rotating_aggregate.get('bit_rpm__avg')
            s_flow_rate_avg_rotating = rotating_aggregate.get('edr_raw__flow_in__avg')
            s_diff_pressure_avg_rotating = rotating_aggregate.get('edr_raw__diff_press__avg')
            s_pump_pressure_avg_rotating = rotating_aggregate.get('edr_raw__pump_press__avg')
            s_top_drive_torque_avg_rotating = rotating_aggregate.get('edr_raw__td_torque__avg')

        surface = {
            "interval_name": s_interval_name,
            "holesize": s_holesize,
            "casing_size": s_casingsize,
            "hole_depth_start": s_hole_depth_start,
            "hole_depth_end": s_hole_depth_end,

            "dt_start": s_dt_start,
            "dt_end": s_dt_end,
            "total_hours": s_total_hours,
            "drill_hours": s_drill_hours,
            "svy_inc_start": s_svy_inc_start,
            "svy_inc_end": s_svy_inc_end,

            "rop_avg": s_rop_avg,

            #Sliding parameters
            "sliding_footage": s_sliding_footage,
            "slide_pct_d": s_slide_pct_d,
            "slide_pct_t": s_slide_pct_t,
            "rop_avg_sliding": s_rop_avg_sliding,
            "wob_avg_sliding": s_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": s_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": s_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": s_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": s_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": s_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": s_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": s_rotating_footage,
            "rotate_pct_d": s_rotate_pct_d,
            "rotate_pct_t": s_rotate_pct_t,
            "rop_avg_rotating": s_rop_avg_rotating,
            "wob_avg_rotating": s_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": s_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": s_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": s_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": s_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": s_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": s_top_drive_torque_avg_rotating,
        }

        return surface


    def get_intermediate(self, obj):

        I1_interval_name = I1_holesize = I1_hole_depth_start = I1_hole_depth_end =I1_casingsize= 0
        I1_dt_start = I1_dt_end = I1_total_hours = I1_drill_hours = I1_svy_inc_start = I1_svy_inc_end = I1_rop_avg = 0

        #sliding parameters
        I1_sliding_footage = I1_slide_pct_d = I1_slide_pct_t = I1_rop_avg_sliding = I1_wob_avg_sliding = 0
        I1_top_drive_rpm_avg_sliding = I1_bit_rpm_avg_sliding = I1_flow_rate_avg_sliding = 0
        I1_diff_pressure_avg_sliding = I1_pump_pressure_avg_sliding = I1_top_drive_torque_avg_sliding = 0

        #rotating parameters
        I1_rotating_footage = I1_rotate_pct_d = I1_rotate_pct_t = I1_rop_avg_rotating = I1_wob_avg_rotating = 0
        I1_top_drive_rpm_avg_rotating = I1_bit_rpm_avg_rotating = I1_flow_rate_avg_rotating = 0
        I1_diff_pressure_avg_rotating = I1_pump_pressure_avg_rotating = I1_top_drive_torque_avg_rotating = 0


        try:
            intermediate_on_uid = Interval.objects.get(name="Intermediate", job=obj.job)
        except:
            intermediate_on_uid = None
        
        if(intermediate_on_uid):
            I1_interval_name = intermediate_on_uid.name
            I1_holesize = intermediate_on_uid.hole_size
            I1_casingsize = intermediate_on_uid.casing_size
            I1_hole_depth_start = intermediate_on_uid.start_depth
            I1_hole_depth_end = intermediate_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=I1_hole_depth_start, edr_raw__hole_depth__lte=I1_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=I1_hole_depth_start, edr_raw__hole_depth__lte=I1_hole_depth_end,slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=I1_hole_depth_start, edr_raw__hole_depth__lte=I1_hole_depth_end,slide_count=0)

            drilled_aggregates = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            I1_dt_start = drilled_aggregates.get('edr_raw__rig_time__min')
            I1_dt_end = drilled_aggregates.get('edr_raw__rig_time__max')
            I1_total_hours = (I1_dt_end-I1_dt_start).total_seconds() / 3600
            I1_drill_hours = len(drilled_on_uid)*obj.data_frequency / 3600
            I1_rop_avg = drilled_aggregates.get('rop_a__avg')


            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))

            I1_sliding_footage = sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum') > 0 else 0
            I1_slide_pct_d = I1_sliding_footage/(I1_hole_depth_end-I1_hole_depth_start) * 100
            I1_slide_pct_t = len(slide_on_uid)*obj.data_frequency/ 3600 / I1_drill_hours
            I1_rop_avg_sliding = sliding_aggregate.get('rop_a__avg')
            I1_wob_avg_sliding = sliding_aggregate.get('edr_raw__wob__avg')
            I1_top_drive_rpm_avg_sliding = sliding_aggregate.get('edr_raw__td_rpm__avg')
            I1_bit_rpm_avg_sliding = sliding_aggregate.get('bit_rpm__avg')
            I1_flow_rate_avg_sliding = sliding_aggregate.get('edr_raw__flow_in__avg')
            I1_diff_pressure_avg_sliding = sliding_aggregate.get('edr_raw__diff_press__avg')
            I1_pump_pressure_avg_sliding = sliding_aggregate.get('edr_raw__pump_press__avg')
            I1_top_drive_torque_avg_sliding = sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I1_rotating_footage = I1_hole_depth_end - I1_hole_depth_start - I1_sliding_footage
            I1_rotate_pct_d = 100 - I1_slide_pct_d
            I1_rotate_pct_t = 100 - I1_slide_pct_t
            I1_rop_avg_rotating = rotating_aggregate.get('rop_a__avg')
            I1_wob_avg_rotating = rotating_aggregate.get('edr_raw__wob__avg')
            I1_top_drive_rpm_avg_rotating = rotating_aggregate.get('edr_raw__td_rpm__avg')
            I1_bit_rpm_avg_rotating = rotating_aggregate.get('bit_rpm__avg')
            I1_flow_rate_avg_rotating = rotating_aggregate.get('edr_raw__flow_in__avg')
            I1_diff_pressure_avg_rotating = rotating_aggregate.get('edr_raw__diff_press__avg')
            I1_pump_pressure_avg_rotating = rotating_aggregate.get('edr_raw__pump_press__avg')
            I1_top_drive_torque_avg_rotating = rotating_aggregate.get('edr_raw__td_torque__avg')

        intermediate = {
            "interval_name": I1_interval_name,
            "holesize": I1_holesize,
            "casing_size": I1_casingsize,
            "hole_depth_start": I1_hole_depth_start,
            "hole_depth_end": I1_hole_depth_end,

            "dt_start": I1_dt_start,
            "dt_end": I1_dt_end,
            "total_hours": I1_total_hours,
            "drill_hours": I1_drill_hours,
            "svy_inc_start": I1_svy_inc_start,
            "svy_inc_end": I1_svy_inc_end,

            "rop_avg": I1_rop_avg,

            #Sliding parameters
            "sliding_footage": I1_sliding_footage,
            "slide_pct_d": I1_slide_pct_d,
            "slide_pct_t": I1_slide_pct_t,
            "rop_avg_sliding": I1_rop_avg_sliding,
            "wob_avg_sliding": I1_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": I1_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": I1_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": I1_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": I1_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": I1_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": I1_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": I1_rotating_footage,
            "rotate_pct_d": I1_rotate_pct_d,
            "rotate_pct_t": I1_rotate_pct_t,
            "rop_avg_rotating": I1_rop_avg_rotating,
            "wob_avg_rotating": I1_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": I1_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": I1_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": I1_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": I1_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": I1_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": I1_top_drive_torque_avg_rotating,
        }

        return intermediate

    def get_curve(self, obj):

        c_interval_name = c_holesize = c_hole_depth_start = c_hole_depth_end =c_casingsize= 0
        c_dt_start= c_dt_end =c_total_hours =c_drill_hours =c_svy_inc_start =c_svy_inc_end =c_rop_avg =0

        #sliding parameters
        c_sliding_footage=c_slide_pct_d=c_slide_pct_t=c_rop_avg_sliding=c_wob_avg_sliding=0
        c_top_drive_rpm_avg_sliding=c_bit_rpm_avg_sliding=c_flow_rate_avg_sliding=0
        c_diff_pressure_avg_sliding=c_pump_pressure_avg_sliding=c_top_drive_torque_avg_sliding=0

        #rotating parameters
        c_rotating_footage=c_rotate_pct_d=c_rotate_pct_t=c_rop_avg_rotating=c_wob_avg_rotating=0
        c_top_drive_rpm_avg_rotating=c_bit_rpm_avg_rotating=c_flow_rate_avg_rotating=c_tfe=0
        c_diff_pressure_avg_rotating=c_pump_pressure_avg_rotating=c_top_drive_torque_avg_rotating=0


        try:
            curve_on_uid = Interval.objects.get(name="Curve", job=obj.job)
        except:
            curve_on_uid = None
        
        if(curve_on_uid):
            c_interval_name = curve_on_uid.name
            c_holesize = curve_on_uid.hole_size
            c_casingsize = curve_on_uid.casing_size
            c_hole_depth_start = curve_on_uid.start_depth
            c_hole_depth_end = curve_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=c_hole_depth_start, edr_raw__hole_depth__lte=c_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=c_hole_depth_start, edr_raw__hole_depth__lte=c_hole_depth_end, slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid, edr_raw__hole_depth__gte=c_hole_depth_start, edr_raw__hole_depth__lte=c_hole_depth_end, slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))
            
            c_dt_start= drilled_aggregate.get('edr_raw__rig_time__min')
            c_dt_end = drilled_aggregate.get('edr_raw__rig_time__max')
            c_total_hours =(c_dt_end-c_dt_start).total_seconds() / 3600
            c_drill_hours =  len(drilled_on_uid)*obj.data_frequency / 3600
            c_rop_avg = drilled_aggregate.get('rop_a__avg')
      
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("slide_value_tf"),Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))

            c_sliding_footage = sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum') > 0 else 0
            c_slide_pct_d = c_sliding_footage / (c_hole_depth_end-c_hole_depth_start) * 100
            c_slide_pct_t = len(slide_on_uid) * obj.data_frequency / 3600 / c_drill_hours
            c_rop_avg_sliding = sliding_aggregate.get('rop_a__avg')
            c_wob_avg_sliding = sliding_aggregate.get('edr_raw__wob__avg')
            c_top_drive_rpm_avg_sliding = sliding_aggregate.get('edr_raw__td_rpm__avg')
            c_bit_rpm_avg_sliding = sliding_aggregate.get('bit_rpm__avg')
            c_flow_rate_avg_sliding = sliding_aggregate.get('edr_raw__flow_in__avg')
            c_diff_pressure_avg_sliding = sliding_aggregate.get('edr_raw__diff_press__avg')
            c_pump_pressure_avg_sliding = sliding_aggregate.get('edr_raw__pump_press__avg')
            c_top_drive_torque_avg_sliding = sliding_aggregate.get('edr_raw__td_torque__avg')
            c_tfe = sliding_aggregate.get('slide_value_tf__sum')/c_sliding_footage*100
            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            c_rotating_footage = c_hole_depth_end-c_hole_depth_start-c_sliding_footage
            c_rotate_pct_d = 100-c_slide_pct_d
            c_rotate_pct_t = 100-c_slide_pct_t
            c_rop_avg_rotating = rotating_aggregate.get('rop_a__avg')
            c_wob_avg_rotating = rotating_aggregate.get('edr_raw__wob__avg')
            c_top_drive_rpm_avg_rotating = rotating_aggregate.get('edr_raw__td_rpm__avg')
            c_bit_rpm_avg_rotating = rotating_aggregate.get('bit_rpm__avg')
            c_flow_rate_avg_rotating = rotating_aggregate.get('edr_raw__flow_in__avg')
            c_diff_pressure_avg_rotating = rotating_aggregate.get('edr_raw__diff_press__avg')
            c_pump_pressure_avg_rotating = rotating_aggregate.get('edr_raw__pump_press__avg')
            c_top_drive_torque_avg_rotating = rotating_aggregate.get('edr_raw__td_torque__avg')

        curve = {
            "interval_name": c_interval_name,
            "holesize": c_holesize,
            "casing_size": c_casingsize,
            "hole_depth_start": c_hole_depth_start,
            "hole_depth_end": c_hole_depth_end,

            "dt_start": c_dt_start,
            "dt_end": c_dt_end,
            "total_hours": c_total_hours,
            "drill_hours": c_drill_hours,
            "svy_inc_start": c_svy_inc_start,
            "svy_inc_end": c_svy_inc_end,

            "rop_avg": c_rop_avg,

            #Sliding parameters
            "sliding_footage": c_sliding_footage,
            "slide_pct_d": c_slide_pct_d,
            "slide_pct_t": c_slide_pct_t,
            "rop_avg_sliding": c_rop_avg_sliding,
            "wob_avg_sliding": c_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": c_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": c_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": c_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": c_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": c_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": c_top_drive_torque_avg_sliding,
            "tool_face_effeciency": c_tfe,
            #Rotating parameters
            "rotating_footage": c_rotating_footage,
            "rotate_pct_d": c_rotate_pct_d,
            "rotate_pct_t": c_rotate_pct_t,
            "rop_avg_rotating": c_rop_avg_rotating,
            "wob_avg_rotating": c_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": c_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": c_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": c_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": c_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": c_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": c_top_drive_torque_avg_rotating,
        }

        return curve

    def get_lateral(self, obj):

        l_interval_name=l_holesize=l_hole_depth_start=l_hole_depth_end =l_casingsize=0
        l_dt_start= l_dt_end =l_total_hours =l_drill_hours =l_svy_inc_start =l_svy_inc_end =l_rop_avg =0

        #sliding parameters
        l_sliding_footage=l_slide_pct_d=l_slide_pct_t=l_rop_avg_sliding=l_wob_avg_sliding=0
        l_top_drive_rpm_avg_sliding=l_bit_rpm_avg_sliding=l_flow_rate_avg_sliding=0
        l_diff_pressure_avg_sliding=l_pump_pressure_avg_sliding=l_top_drive_torque_avg_sliding=0

        #rotating parameters
        l_rotating_footage=l_rotate_pct_d=l_rotate_pct_t=l_rop_avg_rotating=l_wob_avg_rotating=0
        l_top_drive_rpm_avg_rotating=l_bit_rpm_avg_rotating=l_flow_rate_avg_rotating=0
        l_diff_pressure_avg_rotating=l_pump_pressure_avg_rotating=l_top_drive_torque_avg_rotating=0

        try:
            lateral_on_uid = Interval.objects.get(name="Lateral", job=obj.job)
        except:
             lateral_on_uid = None

        
        if(lateral_on_uid):
            l_interval_name=lateral_on_uid.name
            l_holesize=lateral_on_uid.hole_size
            l_casingsize = lateral_on_uid.casing_size
            l_hole_depth_start=lateral_on_uid.start_depth
            l_hole_depth_end =lateral_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=l_hole_depth_start, edr_raw__hole_depth__lte=l_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=l_hole_depth_start, edr_raw__hole_depth__lte=l_hole_depth_end,slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=l_hole_depth_start, edr_raw__hole_depth__lte=l_hole_depth_end,slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            l_dt_start=drilled_aggregate.get('edr_raw__rig_time__min')
            l_dt_end =drilled_aggregate.get('edr_raw__rig_time__max')
            l_total_hours =(l_dt_end-l_dt_start).total_seconds() / 3600
            l_drill_hours =len(drilled_on_uid)*obj.data_frequency/ 3600
            l_rop_avg =drilled_aggregate.get('rop_a__avg')
      
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            l_sliding_footage=sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum')> 0 else 0
            l_slide_pct_d=l_sliding_footage/(l_hole_depth_end-l_hole_depth_start)*100
            l_slide_pct_t=len(slide_on_uid)*obj.data_frequency/ 3600 /l_drill_hours
            l_rop_avg_sliding=sliding_aggregate.get('rop_a__avg')
            l_wob_avg_sliding=sliding_aggregate.get('edr_raw__wob__avg')
            l_top_drive_rpm_avg_sliding=sliding_aggregate.get('edr_raw__td_rpm__avg')
            l_bit_rpm_avg_sliding=sliding_aggregate.get('bit_rpm__avg')
            l_flow_rate_avg_sliding=sliding_aggregate.get('edr_raw__flow_in__avg')
            l_diff_pressure_avg_sliding=sliding_aggregate.get('edr_raw__diff_press__avg')
            l_pump_pressure_avg_sliding=sliding_aggregate.get('edr_raw__pump_press__avg')
            l_top_drive_torque_avg_sliding=sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            l_rotating_footage=l_hole_depth_end-l_hole_depth_start-l_sliding_footage
            l_rotate_pct_d=100-l_slide_pct_d
            l_rotate_pct_t=100-l_slide_pct_t
            l_rop_avg_rotating=rotating_aggregate.get('rop_a__avg')
            l_wob_avg_rotating=rotating_aggregate.get('edr_raw__wob__avg')
            l_top_drive_rpm_avg_rotating=rotating_aggregate.get('edr_raw__td_rpm__avg')
            l_bit_rpm_avg_rotating=rotating_aggregate.get('bit_rpm__avg')
            l_flow_rate_avg_rotating=rotating_aggregate.get('edr_raw__flow_in__avg')
            l_diff_pressure_avg_rotating=rotating_aggregate.get('edr_raw__diff_press__avg')
            l_pump_pressure_avg_rotating=rotating_aggregate.get('edr_raw__pump_press__avg')
            l_top_drive_torque_avg_rotating=rotating_aggregate.get('edr_raw__td_torque__avg')

        lateral = {
            "interval_name": l_interval_name,
            "holesize": l_holesize,
            "casing_size": l_casingsize,
            "hole_depth_start": l_hole_depth_start,
            "hole_depth_end": l_hole_depth_end,

            "dt_start": l_dt_start,
            "dt_end": l_dt_end,
            "total_hours": l_total_hours,
            "drill_hours": l_drill_hours,
            "svy_inc_start": l_svy_inc_start,
            "svy_inc_end": l_svy_inc_end,

            "rop_avg": l_rop_avg,

            #Sliding parameters
            "sliding_footage": l_sliding_footage,
            "slide_pct_d": l_slide_pct_d,
            "slide_pct_t": l_slide_pct_t,
            "rop_avg_sliding": l_rop_avg_sliding,
            "wob_avg_sliding": l_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": l_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": l_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": l_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": l_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": l_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": l_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": l_rotating_footage,
            "rotate_pct_d": l_rotate_pct_d,
            "rotate_pct_t": l_rotate_pct_t,
            "rop_avg_rotating": l_rop_avg_rotating,
            "wob_avg_rotating": l_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": l_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": l_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": l_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": l_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": l_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": l_top_drive_torque_avg_rotating,
        }

        return lateral

    def get_tangent(self, obj):

        t_interval_name=t_holesize=t_hole_depth_start=t_hole_depth_end =t_casingsize=0
        t_dt_start= t_dt_end =t_total_hours =t_drill_hours =t_svy_inc_start =t_svy_inc_end =t_rop_avg =0

        #sliding parameters
        t_sliding_footage=t_slide_pct_d=t_slide_pct_t=t_rop_avg_sliding=t_wob_avg_sliding=0
        t_top_drive_rpm_avg_sliding=t_bit_rpm_avg_sliding=t_flow_rate_avg_sliding=0
        t_diff_pressure_avg_sliding=t_pump_pressure_avg_sliding=t_top_drive_torque_avg_sliding=0

        #rotating parameters
        t_rotating_footage=t_rotate_pct_d=t_rotate_pct_t=t_rop_avg_rotating=t_wob_avg_rotating=0
        t_top_drive_rpm_avg_rotating=t_bit_rpm_avg_rotating=t_flow_rate_avg_rotating=0
        t_diff_pressure_avg_rotating=t_pump_pressure_avg_rotating=t_top_drive_torque_avg_rotating=0

        try:
            tangent_on_uid = Interval.objects.get(name="Tangent", job=obj.job)
        except:
            tangent_on_uid = None
        
        if(tangent_on_uid):
            t_interval_name=tangent_on_uid.name
            t_holesize=tangent_on_uid.hole_size
            t_casingsize = tangent_on_uid.casing_size
            t_hole_depth_start=tangent_on_uid.start_depth
            t_hole_depth_end =tangent_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=t_hole_depth_start, edr_raw__hole_depth__lte=t_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=t_hole_depth_start, edr_raw__hole_depth__lte=t_hole_depth_end,slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=t_hole_depth_start, edr_raw__hole_depth__lte=t_hole_depth_end,slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            t_dt_start=drilled_aggregate.get('edr_raw__rig_time__min')
            t_dt_end =drilled_aggregate.get('edr_raw__rig_time__max')
            t_total_hours =(t_dt_end-t_dt_start).total_seconds() / 3600
            t_drill_hours =len(drilled_on_uid)*obj.data_frequency/ 3600
            t_rop_avg =drilled_aggregate.get('rop_a__avg')
      
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            t_sliding_footage=sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum')> 0 else 0
            t_slide_pct_d=t_sliding_footage/(t_hole_depth_end-t_hole_depth_start)*100
            t_slide_pct_t=len(slide_on_uid)*obj.data_frequency/ 3600 /t_drill_hours
            t_rop_avg_sliding=sliding_aggregate.get('rop_a__avg')
            t_wob_avg_sliding=sliding_aggregate.get('edr_raw__wob__avg')
            t_top_drive_rpm_avg_sliding=sliding_aggregate.get('edr_raw__td_rpm__avg')
            t_bit_rpm_avg_sliding=sliding_aggregate.get('bit_rpm__avg')
            t_flow_rate_avg_sliding=sliding_aggregate.get('edr_raw__flow_in__avg')
            t_diff_pressure_avg_sliding=sliding_aggregate.get('edr_raw__diff_press__avg')
            t_pump_pressure_avg_sliding=sliding_aggregate.get('edr_raw__pump_press__avg')
            t_top_drive_torque_avg_sliding=sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            t_rotating_footage=t_hole_depth_end-t_hole_depth_start-t_sliding_footage
            t_rotate_pct_d=100-t_slide_pct_d
            t_rotate_pct_t=100-t_slide_pct_t
            t_rop_avg_rotating=rotating_aggregate.get('rop_a__avg')
            t_wob_avg_rotating=rotating_aggregate.get('edr_raw__wob__avg')
            t_top_drive_rpm_avg_rotating=rotating_aggregate.get('edr_raw__td_rpm__avg')
            t_bit_rpm_avg_rotating=rotating_aggregate.get('bit_rpm__avg')
            t_flow_rate_avg_rotating=rotating_aggregate.get('edr_raw__flow_in__avg')
            t_diff_pressure_avg_rotating=rotating_aggregate.get('edr_raw__diff_press__avg')
            t_pump_pressure_avg_rotating=rotating_aggregate.get('edr_raw__pump_press__avg')
            t_top_drive_torque_avg_rotating=rotating_aggregate.get('edr_raw__td_torque__avg')

        tangent = {
            "interval_name": t_interval_name,
            "holesize": t_holesize,
            "casing_size": t_casingsize,
            "hole_depth_start": t_hole_depth_start,
            "hole_depth_end": t_hole_depth_end,

            "dt_start": t_dt_start,
            "dt_end": t_dt_end,
            "total_hours": t_total_hours,
            "drill_hours": t_drill_hours,
            "svy_inc_start": t_svy_inc_start,
            "svy_inc_end": t_svy_inc_end,

            "rop_avg": t_rop_avg,

            #Sliding parameters
            "sliding_footage": t_sliding_footage,
            "slide_pct_d": t_slide_pct_d,
            "slide_pct_t": t_slide_pct_t,
            "rop_avg_sliding": t_rop_avg_sliding,
            "wob_avg_sliding": t_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": t_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": t_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": t_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": t_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": t_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": t_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": t_rotating_footage,
            "rotate_pct_d": t_rotate_pct_d,
            "rotate_pct_t": t_rotate_pct_t,
            "rop_avg_rotating": t_rop_avg_rotating,
            "wob_avg_rotating": t_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": t_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": t_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": t_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": t_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": t_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": t_top_drive_torque_avg_rotating,
        }

        return tangent

    def get_intermediate2(self, obj):

        I2_interval_name=I2_holesize=I2_hole_depth_start=I2_hole_depth_end =I2_casingsize=0
        I2_dt_start= I2_dt_end =I2_total_hours =I2_drill_hours =I2_svy_inc_start =I2_svy_inc_end =I2_rop_avg =0

        #sliding parameters
        I2_sliding_footage=I2_slide_pct_d=I2_slide_pct_t=I2_rop_avg_sliding=I2_wob_avg_sliding=0
        I2_top_drive_rpm_avg_sliding=I2_bit_rpm_avg_sliding=I2_flow_rate_avg_sliding=0
        I2_diff_pressure_avg_sliding=I2_pump_pressure_avg_sliding=I2_top_drive_torque_avg_sliding=0

        #rotating parameters
        I2_rotating_footage=I2_rotate_pct_d=I2_rotate_pct_t=I2_rop_avg_rotating=I2_wob_avg_rotating=0
        I2_top_drive_rpm_avg_rotating=I2_bit_rpm_avg_rotating=I2_flow_rate_avg_rotating=0
        I2_diff_pressure_avg_rotating=I2_pump_pressure_avg_rotating=I2_top_drive_torque_avg_rotating=0


        try:
            intermediate2_on_uid = Interval.objects.get(name="2nd Intermediate", job=obj.job)
        except:
            intermediate2_on_uid = None
        
        
        if(intermediate2_on_uid):
            I2_interval_name=intermediate2_on_uid.name
            I2_holesize=intermediate2_on_uid.hole_size
            I2_casingsize = intermediate2_on_uid.casing_size
            I2_hole_depth_start=intermediate2_on_uid.start_depth
            I2_hole_depth_end =intermediate2_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I2_hole_depth_start, edr_raw__hole_depth__lte=I2_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I2_hole_depth_start, edr_raw__hole_depth__lte=I2_hole_depth_end,slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I2_hole_depth_start, edr_raw__hole_depth__lte=I2_hole_depth_end,slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            I2_dt_start=drilled_aggregate.get('edr_raw__rig_time__min')
            I2_dt_end =drilled_aggregate.get('edr_raw__rig_time__max')
            I2_total_hours =(I2_dt_end-I2_dt_start).total_seconds() / 3600
            I2_drill_hours =len(drilled_on_uid)*obj.data_frequency/ 3600
            I2_rop_avg =drilled_aggregate.get('rop_a__avg')
      
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I2_sliding_footage=sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum')> 0 else 0
            I2_slide_pct_d=I2_sliding_footage/(I2_hole_depth_end-I2_hole_depth_start)*100
            I2_slide_pct_t=len(slide_on_uid)*obj.data_frequency/ 3600 /I2_drill_hours
            I2_rop_avg_sliding=sliding_aggregate.get('rop_a__avg')
            I2_wob_avg_sliding=sliding_aggregate.get('edr_raw__wob__avg')
            I2_top_drive_rpm_avg_sliding=sliding_aggregate.get('edr_raw__td_rpm__avg')
            I2_bit_rpm_avg_sliding=sliding_aggregate.get('bit_rpm__avg')
            I2_flow_rate_avg_sliding=sliding_aggregate.get('edr_raw__flow_in__avg')
            I2_diff_pressure_avg_sliding=sliding_aggregate.get('edr_raw__diff_press__avg')
            I2_pump_pressure_avg_sliding=sliding_aggregate.get('edr_raw__pump_press__avg')
            I2_top_drive_torque_avg_sliding=sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I2_rotating_footage=I2_hole_depth_end-I2_hole_depth_start-I2_sliding_footage
            I2_rotate_pct_d=100-I2_slide_pct_d
            I2_rotate_pct_t=100-I2_slide_pct_t
            I2_rop_avg_rotating=rotating_aggregate.get('rop_a__avg')
            I2_wob_avg_rotating=rotating_aggregate.get('edr_raw__wob__avg')
            I2_top_drive_rpm_avg_rotating=rotating_aggregate.get('edr_raw__td_rpm__avg')
            I2_bit_rpm_avg_rotating=rotating_aggregate.get('bit_rpm__avg')
            I2_flow_rate_avg_rotating=rotating_aggregate.get('edr_raw__flow_in__avg')
            I2_diff_pressure_avg_rotating=rotating_aggregate.get('edr_raw__diff_press__avg')
            I2_pump_pressure_avg_rotating=rotating_aggregate.get('edr_raw__pump_press__avg')
            I2_top_drive_torque_avg_rotating=rotating_aggregate.get('edr_raw__td_torque__avg')

        intermediate2 = {
            "interval_name": I2_interval_name,
            "holesize": I2_holesize,
            "casing_size": I2_casingsize,
            "hole_depth_start": I2_hole_depth_start,
            "hole_depth_end": I2_hole_depth_end,

            "dt_start": I2_dt_start,
            "dt_end": I2_dt_end,
            "total_hours": I2_total_hours,
            "drill_hours": I2_drill_hours,
            "svy_inc_start": I2_svy_inc_start,
            "svy_inc_end": I2_svy_inc_end,

            "rop_avg": I2_rop_avg,

            #Sliding parameters
            "sliding_footage": I2_sliding_footage,
            "slide_pct_d": I2_slide_pct_d,
            "slide_pct_t": I2_slide_pct_t,
            "rop_avg_sliding": I2_rop_avg_sliding,
            "wob_avg_sliding": I2_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": I2_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": I2_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": I2_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": I2_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": I2_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": I2_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": I2_rotating_footage,
            "rotate_pct_d": I2_rotate_pct_d,
            "rotate_pct_t": I2_rotate_pct_t,
            "rop_avg_rotating": I2_rop_avg_rotating,
            "wob_avg_rotating": I2_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": I2_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": I2_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": I2_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": I2_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": I2_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": I2_top_drive_torque_avg_rotating,
        }

        return intermediate2

    def get_intermediate3(self, obj):

        I3_interval_name=I3_holesize=I3_hole_depth_start=I3_hole_depth_end =I3_casingsize=0
        I3_dt_start= I3_dt_end =I3_total_hours =I3_drill_hours =I3_svy_inc_start =I3_svy_inc_end =I3_rop_avg =0

        #sliding parameters
        I3_sliding_footage=I3_slide_pct_d=I3_slide_pct_t=I3_rop_avg_sliding=I3_wob_avg_sliding=0
        I3_top_drive_rpm_avg_sliding=I3_bit_rpm_avg_sliding=I3_flow_rate_avg_sliding=0
        I3_diff_pressure_avg_sliding=I3_pump_pressure_avg_sliding=I3_top_drive_torque_avg_sliding=0

        #rotating parameters
        I3_rotating_footage=I3_rotate_pct_d=I3_rotate_pct_t=I3_rop_avg_rotating=I3_wob_avg_rotating=0
        I3_top_drive_rpm_avg_rotating=I3_bit_rpm_avg_rotating=I3_flow_rate_avg_rotating=0
        I3_diff_pressure_avg_rotating=I3_pump_pressure_avg_rotating=I3_top_drive_torque_avg_rotating=0


        try:
            intermediate3_on_uid = Interval.objects.get(name="3rd Intermediate", job=obj.job)
        except:
            intermediate3_on_uid = None
        
        if(intermediate3_on_uid):
            I3_interval_name=intermediate3_on_uid.name
            I3_holesize=intermediate3_on_uid.hole_size
            I3_casingsize = intermediate3_on_uid.casing_size
            I3_hole_depth_start=intermediate3_on_uid.start_depth
            I3_hole_depth_end =intermediate3_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I3_hole_depth_start, edr_raw__hole_depth__lte=I3_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I3_hole_depth_start, edr_raw__hole_depth__lte=I3_hole_depth_end,slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I3_hole_depth_start, edr_raw__hole_depth__lte=I3_hole_depth_end,slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            I3_dt_start=drilled_aggregate.get('edr_raw__rig_time__min')
            I3_dt_end =drilled_aggregate.get('edr_raw__rig_time__max')
            I3_total_hours =(I3_dt_end-I3_dt_start).total_seconds() / 3600
            I3_drill_hours =len(drilled_on_uid)*obj.data_frequency/ 3600
            I3_rop_avg =drilled_aggregate.get('rop_a__avg')
      
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I3_sliding_footage=sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum')> 0 else 0
            I3_slide_pct_d=I3_sliding_footage/(I3_hole_depth_end-I3_hole_depth_start)*100
            I3_slide_pct_t=len(slide_on_uid)*obj.data_frequency/ 3600 /I3_drill_hours
            I3_rop_avg_sliding=sliding_aggregate.get('rop_a__avg')
            I3_wob_avg_sliding=sliding_aggregate.get('edr_raw__wob__avg')
            I3_top_drive_rpm_avg_sliding=sliding_aggregate.get('edr_raw__td_rpm__avg')
            I3_bit_rpm_avg_sliding=sliding_aggregate.get('bit_rpm__avg')
            I3_flow_rate_avg_sliding=sliding_aggregate.get('edr_raw__flow_in__avg')
            I3_diff_pressure_avg_sliding=sliding_aggregate.get('edr_raw__diff_press__avg')
            I3_pump_pressure_avg_sliding=sliding_aggregate.get('edr_raw__pump_press__avg')
            I3_top_drive_torque_avg_sliding=sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I3_rotating_footage=I3_hole_depth_end-I3_hole_depth_start-I3_sliding_footage
            I3_rotate_pct_d=100-I3_slide_pct_d
            I3_rotate_pct_t=100-I3_slide_pct_t
            I3_rop_avg_rotating=rotating_aggregate.get('rop_a__avg')
            I3_wob_avg_rotating=rotating_aggregate.get('edr_raw__wob__avg')
            I3_top_drive_rpm_avg_rotating=rotating_aggregate.get('edr_raw__td_rpm__avg')
            I3_bit_rpm_avg_rotating=rotating_aggregate.get('bit_rpm__avg')
            I3_flow_rate_avg_rotating=rotating_aggregate.get('edr_raw__flow_in__avg')
            I3_diff_pressure_avg_rotating=rotating_aggregate.get('edr_raw__diff_press__avg')
            I3_pump_pressure_avg_rotating=rotating_aggregate.get('edr_raw__pump_press__avg')
            I3_top_drive_torque_avg_rotating=rotating_aggregate.get('edr_raw__td_torque__avg')

        intermediate3 = {
            "interval_name": I3_interval_name,
            "holesize": I3_holesize,
            "casing_size": I3_casingsize,
            "hole_depth_start": I3_hole_depth_start,
            "hole_depth_end": I3_hole_depth_end,

            "dt_start": I3_dt_start,
            "dt_end": I3_dt_end,
            "total_hours": I3_total_hours,
            "drill_hours": I3_drill_hours,
            "svy_inc_start": I3_svy_inc_start,
            "svy_inc_end": I3_svy_inc_end,

            "rop_avg": I3_rop_avg,

            #Sliding parameters
            "sliding_footage": I3_sliding_footage,
            "slide_pct_d": I3_slide_pct_d,
            "slide_pct_t": I3_slide_pct_t,
            "rop_avg_sliding": I3_rop_avg_sliding,
            "wob_avg_sliding": I3_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": I3_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": I3_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": I3_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": I3_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": I3_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": I3_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": I3_rotating_footage,
            "rotate_pct_d": I3_rotate_pct_d,
            "rotate_pct_t": I3_rotate_pct_t,
            "rop_avg_rotating": I3_rop_avg_rotating,
            "wob_avg_rotating": I3_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": I3_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": I3_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": I3_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": I3_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": I3_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": I3_top_drive_torque_avg_rotating,
        }

        return intermediate3

    def get_intermediate4(self, obj):

        I4_interval_name=I4_holesize=I4_hole_depth_start=I4_hole_depth_end=I4_casingsize=0
        I4_dt_start= I4_dt_end =I4_total_hours =I4_drill_hours =I4_svy_inc_start =I4_svy_inc_end =I4_rop_avg =0

        #sliding parameters
        I4_sliding_footage=I4_slide_pct_d=I4_slide_pct_t=I4_rop_avg_sliding=I4_wob_avg_sliding=0
        I4_top_drive_rpm_avg_sliding=I4_bit_rpm_avg_sliding=I4_flow_rate_avg_sliding=0
        I4_diff_pressure_avg_sliding=I4_pump_pressure_avg_sliding=I4_top_drive_torque_avg_sliding=0

        #rotating parameters
        I4_rotating_footage=I4_rotate_pct_d=I4_rotate_pct_t=I4_rop_avg_rotating=I4_wob_avg_rotating=0
        I4_top_drive_rpm_avg_rotating=I4_bit_rpm_avg_rotating=I4_flow_rate_avg_rotating=0
        I4_diff_pressure_avg_rotating=I4_pump_pressure_avg_rotating=I4_top_drive_torque_avg_rotating=0


        try:
            intermediate4_on_uid = Interval.objects.get(name="4th Intermediate", job=obj.job)
        except:
            intermediate4_on_uid = None
        
        if(intermediate4_on_uid):
            I4_interval_name=intermediate4_on_uid.name
            I4_holesize=intermediate4_on_uid.hole_size
            I4_casingsize= intermediate4_on_uid.casing_size
            I4_hole_depth_start=intermediate4_on_uid.start_depth
            I4_hole_depth_end =intermediate4_on_uid.end_depth

            drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I4_hole_depth_start, edr_raw__hole_depth__lte=I4_hole_depth_end)
            slide_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I4_hole_depth_start, edr_raw__hole_depth__lte=I4_hole_depth_end,slide_count__gt=0)
            rotate_on_uid = EDRDrilled.objects.filter(uid=obj.uid,edr_raw__hole_depth__gte=I4_hole_depth_start, edr_raw__hole_depth__lte=I4_hole_depth_end,slide_count=0)

            drilled_aggregate = drilled_on_uid.aggregate(Min("edr_raw__rig_time"), Max("edr_raw__rig_time"), Avg("rop_a"))

            I4_dt_start=drilled_aggregate.get('edr_raw__rig_time__min')
            I4_dt_end =drilled_aggregate.get('edr_raw__rig_time__max')
            I4_total_hours =(I4_dt_end-I4_dt_start).total_seconds() / 3600
            I4_drill_hours =len(drilled_on_uid)*obj.data_frequency/ 3600
            I4_rop_avg =drilled_aggregate.get('rop_a__avg')
      
            #sliding parameters
            sliding_aggregate = slide_on_uid.aggregate(Sum("drilled_ft"), Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I4_sliding_footage=sliding_aggregate.get('drilled_ft__sum') if sliding_aggregate.get('drilled_ft__sum') and sliding_aggregate.get('drilled_ft__sum')> 0 else 0
            I4_slide_pct_d=I4_sliding_footage/(I4_hole_depth_end-I4_hole_depth_start)*100
            I4_slide_pct_t=len(slide_on_uid)*obj.data_frequency/ 3600 /I4_drill_hours
            I4_rop_avg_sliding=sliding_aggregate.get('rop_a__avg')
            I4_wob_avg_sliding=sliding_aggregate.get('edr_raw__wob__avg')
            I4_top_drive_rpm_avg_sliding=sliding_aggregate.get('edr_raw__td_rpm__avg')
            I4_bit_rpm_avg_sliding=sliding_aggregate.get('bit_rpm__avg')
            I4_flow_rate_avg_sliding=sliding_aggregate.get('edr_raw__flow_in__avg')
            I4_diff_pressure_avg_sliding=sliding_aggregate.get('edr_raw__diff_press__avg')
            I4_pump_pressure_avg_sliding=sliding_aggregate.get('edr_raw__pump_press__avg')
            I4_top_drive_torque_avg_sliding=sliding_aggregate.get('edr_raw__td_torque__avg')

            #rotating parameters
            rotating_aggregate = rotate_on_uid.aggregate(Avg("rop_a"), Avg("edr_raw__wob"), Avg("edr_raw__td_rpm"), Avg("bit_rpm"), Avg("edr_raw__flow_in"), 
                                                        Avg("edr_raw__diff_press"), Avg("edr_raw__pump_press"), Avg("edr_raw__td_torque"))
            I4_rotating_footage=I4_hole_depth_end-I4_hole_depth_start-I4_sliding_footage
            I4_rotate_pct_d=100-I4_slide_pct_d
            I4_rotate_pct_t=100-I4_slide_pct_t
            I4_rop_avg_rotating=rotating_aggregate.get('rop_a__avg')
            I4_wob_avg_rotating=rotating_aggregate.get('edr_raw__wob__avg')
            I4_top_drive_rpm_avg_rotating=rotating_aggregate.get('edr_raw__td_rpm__avg')
            I4_bit_rpm_avg_rotating=rotating_aggregate.get('bit_rpm__avg')
            I4_flow_rate_avg_rotating=rotating_aggregate.get('edr_raw__flow_in__avg')
            I4_diff_pressure_avg_rotating=rotating_aggregate.get('edr_raw__diff_press__avg')
            I4_pump_pressure_avg_rotating=rotating_aggregate.get('edr_raw__pump_press__avg')
            I4_top_drive_torque_avg_rotating=rotating_aggregate.get('edr_raw__td_torque__avg')

        intermediate4 = {
            "interval_name": I4_interval_name,
            "holesize": I4_holesize,
            "casing_size": I4_casingsize,
            "hole_depth_start": I4_hole_depth_start,
            "hole_depth_end": I4_hole_depth_end,

            "dt_start": I4_dt_start,
            "dt_end": I4_dt_end,
            "total_hours": I4_total_hours,
            "drill_hours": I4_drill_hours,
            "svy_inc_start": I4_svy_inc_start,
            "svy_inc_end": I4_svy_inc_end,

            "rop_avg": I4_rop_avg,

            #Sliding parameters
            "sliding_footage": I4_sliding_footage,
            "slide_pct_d": I4_slide_pct_d,
            "slide_pct_t": I4_slide_pct_t,
            "rop_avg_sliding": I4_rop_avg_sliding,
            "wob_avg_sliding": I4_wob_avg_sliding,
            "top_drive_rpm_avg_sliding": I4_top_drive_rpm_avg_sliding,
            "bit_rpm_avg_sliding": I4_bit_rpm_avg_sliding,
            "flow_rate_avg_sliding": I4_flow_rate_avg_sliding,
            "diff_pressure_avg_sliding": I4_diff_pressure_avg_sliding,
            "pump_pressure_avg_sliding": I4_pump_pressure_avg_sliding,
            "top_drive_torque_avg_sliding": I4_top_drive_torque_avg_sliding,

            #Rotating parameters
            "rotating_footage": I4_rotating_footage,
            "rotate_pct_d": I4_rotate_pct_d,
            "rotate_pct_t": I4_rotate_pct_t,
            "rop_avg_rotating": I4_rop_avg_rotating,
            "wob_avg_rotating": I4_wob_avg_rotating,
            "top_drive_rpm_avg_rotating": I4_top_drive_rpm_avg_rotating,
            "bit_rpm_avg_rotating": I4_bit_rpm_avg_rotating,
            "flow_rate_avg_rotating": I4_flow_rate_avg_rotating,
            "diff_pressure_avg_rotating": I4_diff_pressure_avg_rotating,
            "pump_pressure_avg_rotating": I4_pump_pressure_avg_rotating,
            "top_drive_torque_avg_rotating": I4_top_drive_torque_avg_rotating,
        }

        return intermediate4
    class Meta:
        model = WellConnector
        fields = ('id', 'job', 'surface','intermediate','curve','lateral','tangent', 'intermediate2','intermediate3','intermediate4', 'uid')
        read_only_field = ('id', 'job')


class EDRCXNSerializer(serializers.ModelSerializer):
    # job = serializers.SlugRelatedField(
    #     queryset=Job.objects.all(), slug_field='id')
    edr_raw = serializers.SlugRelatedField(
        queryset=EDRRaw.objects.all(), slug_field='id')

    class Meta:
        model = EDRCXN
        fields = '__all__'
        read_only_field = ('id',)


class EDRTripSerializer(serializers.ModelSerializer):
    # job = serializers.SlugRelatedField(
    #     queryset=Job.objects.all(), slug_field='id')
    edr_raw = serializers.SlugRelatedField(
        queryset=EDRRaw.objects.all(), slug_field='id')
    bha = serializers.SlugRelatedField(
        queryset=Bha.objects.all(), slug_field='id')
    interval = serializers.SlugRelatedField(
        queryset=Interval.objects.all(), slug_field='id')

    class Meta:
        model = EDRTrip
        fields = '__all__'
        read_only_field = ('id',)


class EDRCommentSerializer(serializers.ModelSerializer):
    # job = serializers.SlugRelatedField(
    #     queryset=Job.objects.all(), slug_field='id')

    class Meta:
        model = EDRComment
        fields = '__all__'
        read_only_field = ('id',)

class RigStateSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')
    rigstates = serializers.SerializerMethodField(read_only=True)

    def get_rigstates(self, obj):
        hours=[]
        level=[]
        upper_level=[]
        cxn_time = 0
        
        processed_on_uid = EDRProcessed.objects.filter(uid=obj.uid)
        circ_on_uid = EDRProcessed.objects.filter(uid=obj.uid,rig_activity2__lte=3,rig_activity2__gte=2,trip_out_number__lte=0,trip_in_number__lte=0)
        idle_on_uid = EDRProcessed.objects.filter(uid=obj.uid,rig_activity2=7,trip_out_number__lte=0,trip_in_number__lte=0)
        drilled_on_uid = EDRDrilled.objects.filter(uid=obj.uid)
        slid_on_uid = EDRDrilled.objects.filter(uid=obj.uid,slide_count__gt=0)
        cxn_on_uid = EDRCXN.objects.filter(uid=obj.uid)
        print(drilled_on_uid)
        total_well_time =round((processed_on_uid.count()*obj.data_frequency/3600),1)
        circ_time =round((circ_on_uid.count()*obj.data_frequency/3600),1)
        idle_time =round((idle_on_uid.count()*obj.data_frequency/3600),1)
        drill_time =round((drilled_on_uid.count()*obj.data_frequency/3600),1)
        slide_time =round((slid_on_uid.count()*obj.data_frequency/3600),1)
        rotate_time =drill_time-slide_time
        if cxn_on_uid:
            cxn_time = round((cxn_on_uid.aggregate(Sum('total_time')).get('total_time__sum')/60),1)


        hours = list(hours)
        level = list(level)
        upper_level = list(upper_level)

        #trips = EDRTrip.objects.filter(uid=obj, trip_direction=True, casing=False)
        trip_in_on_uid = EDRTrip.objects.filter(uid=obj.uid, trip_direction=True, casing=False)
        trip_out_on_uid = EDRTrip.objects.filter(uid=obj.uid, trip_direction=False, casing=False)
        casing_on_uid = EDRTrip.objects.filter(uid=obj.uid, trip_direction=True, casing=True)
        


        trip_in_depth = 0
        trip_in_time = 0
        trip_out_depth = 0
        trip_out_time = 0
        casing_time = 0

        for item in casing_on_uid:
            casing_time = (item.end_time-item.start_time).total_seconds()/3600 + casing_time

        for item in trip_in_on_uid:
            trip_in_time = (item.end_time-item.start_time).total_seconds()/3600 + trip_in_time


        for item in trip_out_on_uid:
            trip_out_time = (item.end_time-item.start_time).total_seconds()/3600 + trip_out_time


        trip_in_time = round(trip_in_time +.1,1)
        trip_out_time = round(trip_out_time +.1,1)
        casing_time =  round((casing_time)+.1,1)
        tripping_time =  round((trip_in_time+ trip_out_time + casing_time+.1),1)
        und_time = round((float(total_well_time)-float(drill_time) - float(tripping_time) - float(cxn_time)- float(circ_time)- float(idle_time)-.15),1)



        rigstates = {
            "slide": slide_time,
            "rotate": rotate_time,
            "connection": cxn_time,
            "circulating": circ_time,
            "trip_in": trip_in_time,
            "trip_out": trip_out_time,
            "casing": casing_time,
        }

        return rigstates
        
    class Meta:
        model = WellConnector
        fields = ('id', 'job', 'rigstates', 'uid')
        read_only_field = ("__all__")
