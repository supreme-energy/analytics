from rest_framework import serializers, status
import datetime
from django.db.models import Sum
from jobs.models import (Job, Interval, WellConnector, Formation)


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('id', 'creation_date')
        extra_kwargs = {
            # Can be set to default
            'type': {'allow_null': True, 'required': False},
            'well_api': {'allow_null': True, 'required': False},
            'spud_date': {'allow_null': True, 'required': False},
            'end_date': {'allow_null': True, 'required': False}
        }


class WellConnectorSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id', required=False)

    class Meta:
        model = WellConnector
        fields = '__all__'
        read_only_fields = ('id',)
        extra_kwargs = {
            'well_name': {'allow_null': True, 'required': False},
            'rig_name': {'allow_null': True, 'required': False},
            'data_frequency': {'allow_null': True, 'required': False},
            'url': {'allow_null': True, 'required': False},
            'username': {'allow_null': True, 'required': False},
            'password': {'allow_null': True, 'required': False},
        }


class FormationSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')

    class Meta:
        model = Formation
        fields = '__all__'
        read_only_fields = ('id',)
        extra_kwargs = {
            'rock_type': {'allow_null': True, 'required': False},
            'pore_pressure': {'allow_null': True, 'required': False},
            'mud_weight': {'allow_null': True, 'required': False}
        }


class IntervalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interval
        fields = '__all__'
        read_only_fields = ('id',)
        extra_kwargs = {
            'hole_size': {'allow_null': True, 'required': False},
            'casing_size': {'allow_null': True, 'required': False}
        }
