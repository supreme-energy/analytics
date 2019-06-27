from rest_framework import serializers, status

from django.contrib.auth.models import User
from personnel.models import Person
from jobs.models import Job


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')
        read_only_fields = ('id', 'username')


class PersonSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(), slug_field='id', required=False)

    class Meta:
        model = Person
        fields = '__all__'
        read_only_fields = ('id',)
