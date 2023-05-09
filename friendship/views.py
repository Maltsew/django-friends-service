from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework import viewsets

# Create your views here.
from .models import CustomUser
from .serializers import RegisterSerializer
from rest_framework import generics


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
