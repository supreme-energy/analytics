from rest_framework import serializers, status

from plans.models import Plan
from jobs.models import Job


class PlanSerializer(serializers.ModelSerializer):
    job = serializers.SlugRelatedField(
        queryset=Job.objects.all(), slug_field='id')

    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ('creation_date',)
        extra_kwargs = {
            # Can be set to default
            'depth_in_zone': {'allow_null': True, 'required': False},
            'zero_vs': {'allow_null': True, 'required': False},
            'step_out': {'allow_null': True, 'required': False},
            'tie_in_depth': {'allow_null': True, 'required': False},
            'vsplane': {'allow_null': True, 'required': False}
        }
