from rest_framework import serializers, status
from bhas.models import Bha
from jobs.models import Job, Interval, Formation, WellConnector
from edrs.models import (EDRRaw, EDRScoutMotor, EDRProcessed,
                         EDRCXN, EDRComment, EDRTrip, EDRDrilled)
from surveys.models import Survey
import json


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
        read_only_field = ('id',)


class EDRScoutMotorSerializer(serializers.ModelSerializer):
    # job = serializers.SlugRelatedField(
    #     queryset=Job.objects.all(), slug_field='id')
    interval = serializers.SlugRelatedField(
        queryset=Interval.objects.all(), slug_field='id')
    formation = serializers.SlugRelatedField(
        queryset=Formation.objects.all(), slug_field='id')
    bha = serializers.SlugRelatedField(
        queryset=Bha.objects.all(), slug_field='id')
    edrraw = serializers.SlugRelatedField(
        queryset=EDRRaw.objects.all(), slug_field='id')
    edrprocessed = serializers.SlugRelatedField(
        queryset=EDRProcessed.objects.all(), slug_field='id')

    class Meta:
        model = EDRScoutMotor
        fields = '__all__'
        read_only_field = ('id',)


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
    edrprocessed = serializers.SlugRelatedField(
        queryset=EDRProcessed.objects.all(), slug_field='id')
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
