from django.shortcuts import render
from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from . import serializers
from django.db import IntegrityError
from psycopg2.errors import UniqueViolation

# Create your views here.
from .models import User, FriendshipRequest
from .serializers import RegisterSerializer, FriendshipRequestSerializer
from rest_framework import generics
from rest_framework.views import APIView


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class CreateFriendRequestView(generics.ListCreateAPIView):
    queryset = FriendshipRequest.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = FriendshipRequestSerializer

    def post(self, request, *args, **kwargs):
        try:
            to_user = User.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist as e:
            return Response(
                {'message': str(e)},
                status.HTTP_404_NOT_FOUND
            )
        try:
            friend_obj = FriendshipRequest.objects.create(
            from_user=request.user,
            to_user=to_user,
        request_status=2)
            return Response(
                FriendshipRequestSerializer(friend_obj).data,
                status.HTTP_201_CREATED
            )
        except (IntegrityError, UniqueViolation) as e:
            return Response(
                {'message': str(e)},
                status.HTTP_400_BAD_REQUEST
            )