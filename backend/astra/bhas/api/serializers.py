from rest_framework import serializers, status

from bhas.models import Bha
from jobs.models import Job


class BhaSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')

    class Meta:
        model = Bha
        fields = '__all__'
        read_only_fields = ('id', 'creation_date')
        extra_kwargs = {
            'bha_number': {'allow_null': True, 'required': False},
            'depth_out': {'allow_null': True, 'required': False},
            'time_in': {'allow_null': True, 'required': False},
            'time_out': {'allow_null': True, 'required': False},
            'drill_time_start': {'allow_null': True, 'required': False},
            'drill_time_end': {'allow_null': True, 'required': False},
        }
