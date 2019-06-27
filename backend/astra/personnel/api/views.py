from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from django.contrib.auth.models import User
from personnel.models import Person
from .serializers import PersonSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'


class PersonViewSet(viewsets.ModelViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_fields = '__all__'
