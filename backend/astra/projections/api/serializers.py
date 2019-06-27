from rest_framework import serializers, status

from projections.models import Projection
from jobs.models import Job
from personnel.models import Person


class ProjectionSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')

    class Meta:
        model = Projection
        fields = '__all__'
        read_only_fields = ('creation_date', 'number', 'active')
        extra_kwargs = {
            'md': {'allow_null': True, 'required': False},
            'inc': {'allow_null': True, 'required': False},
            'azi': {'allow_null': True, 'required': False},
            'vertical_section': {'allow_null': True, 'required': False},
            'my': {'allow_null': True, 'required': False},
            'bitto_sensor': {'allow_null': True, 'required': False},
            'sli_legth': {'allow_null': True, 'required': False},
        }
