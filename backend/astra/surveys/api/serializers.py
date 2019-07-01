from rest_framework import serializers, status
from math import radians, cos, sin

from surveys.models import Survey
from jobs.models import Job
from plans.models import Plan


class SurveySerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')
    

    class Meta:
        model = Survey
        fields = '__all__'
        read_only_fields = ('creation_date', 'number', 'active')
        extra_kwargs = {
            'mag_total': {'allow_null': True, 'required': False},
            'grav_total': {'allow_null': True, 'required': False},
            'dip': {'allow_null': True, 'required': False},
            'temp': {'allow_null': True, 'required': False},
            'zero_vs': {'allow_null': True, 'required': False},
            'uid': {'allow_null': True, 'required': False},
            'rig_time': {'allow_null': True, 'required': False},
        }
