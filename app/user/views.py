# from django.shortcuts import render
from . import serializers
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework import generics


class CreateUserView(generics.CreateAPIView):
    """ Create a new user in the new system"""
    serializer_class = serializers.UserSerializer


class CreateTokenView(ObtainAuthToken):
    """ Create a new token for a user """

    serializer_class = serializers.AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
