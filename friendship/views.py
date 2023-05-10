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
from .models import User, FriendshipRequest, Friends
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


class AcceptFriendRequestView(generics.ListCreateAPIView):
    """
    Принять заявку в друзья
    """
    queryset = FriendshipRequest.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = FriendshipRequestSerializer

    def put(self, request, *args, **kwargs):
        """
        : kwargs : содержит id заявки, которую нужно принять
        : to_user : всегда request.user
        : from_user : любой другой пользователь
        При переходе по эндпоинту, to_user проверяет, есть ли для него заявка в друзья
        если есть, она принимается, заявка удаляется а данные пользователи становятся друзьями
        """
        try:
            # получаем id заявки в друзья
            friend_request = FriendshipRequest.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist as e:
            return Response(
                {'message': str(e)},
                status.HTTP_404_NOT_FOUND
            )
        to_user = request.user
        if to_user.is_anonymous:
            return Response(
                {'message': "UNAUTHORIZED"},
                status.HTTP_401_UNAUTHORIZED
            )
        # если заявка адресована request.user
        if friend_request.to_user == to_user:
            # статус заявки обновлен на 3 (принята)
            FriendshipRequest.objects.filter(pk=kwargs['pk']).update(request_status=3)
            accepted_request = FriendshipRequest.objects.get(pk=kwargs['pk'])
            try:
                # если заявка принята - создаем дружбу
                Friends.objects.create(from_user=friend_request.from_user, to_user=to_user)
            # если уже друзья - обрабатываем как 400
            # TODO создать ошибку по условию "уже друзья"
            except (IntegrityError, UniqueViolation) as e:
                return Response(
                    {'message': str(e)},
                    status.HTTP_400_BAD_REQUEST
                )
            return Response(
                FriendshipRequestSerializer(accepted_request).data,
                status.HTTP_200_OK
            )
        # если по эндпоинту обратился user1, a to_user!=user1, выкидываем BAD REQUEST
        else:
            return Response(
                {'message'},
                status.HTTP_400_BAD_REQUEST
            )


class RejectFriendRequestView(generics.ListCreateAPIView):
    """
    Отклонить заявку в друзья
    """
    queryset = FriendshipRequest.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = FriendshipRequestSerializer

    def put(self, request, *args, **kwargs):
        """
        : kwargs : содержит id заявки, которую нужно принять
        : to_user : всегда request.user
        : from_user : любой другой пользователь
        При переходе по эндпоинту, to_user проверяет, есть ли для него заявка в друзья
        если есть, он ее отклоняет
        """
        try:
            # получаем id заявки в друзья
            friend_request = FriendshipRequest.objects.get(pk=kwargs['pk'])
        except ObjectDoesNotExist as e:
            return Response(
                {'message': str(e)},
                status.HTTP_404_NOT_FOUND
            )
        to_user = request.user
        if to_user.is_anonymous:
            return Response(
                {'message': "UNAUTHORIZED"},
                status.HTTP_401_UNAUTHORIZED
            )
        # если заявка адресована request.user
        if friend_request.to_user == to_user:
            # статус заявки обновлен на 4 (отклонена)
            FriendshipRequest.objects.filter(pk=kwargs['pk']).update(request_status=4)
            rejected_request = FriendshipRequest.objects.get(pk=kwargs['pk'])
            return Response(
                FriendshipRequestSerializer(rejected_request).data,
                status.HTTP_200_OK
            )
        # если по эндпоинту обратился user1, a to_user!=user1, выкидываем BAD REQUEST
        else:
            return Response(
                {'message'},
                status.HTTP_400_BAD_REQUEST
            )


class IncomingFriendRequestView(generics.ListCreateAPIView):
    """
    Входящие заявки в друзья
    """
    queryset = FriendshipRequest.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = FriendshipRequestSerializer

    def get(self, request, *args, **kwargs):
        """
        Получить входящие заявки в друзья для user
        """
        to_user = request.user
        if to_user.is_anonymous:
            return Response(
                {'message': "UNAUTHORIZED"},
                status.HTTP_401_UNAUTHORIZED
            )
        # получаем все заявки в друзья, в которых to_user = request.user
        incoming_requests = FriendshipRequest.objects.filter(to_user=to_user)
        if not incoming_requests:
            return Response(
                    {'message': "NOT FOUND"},
                    status.HTTP_404_NOT_FOUND
                )
        return Response(
            FriendshipRequestSerializer(incoming_requests, many=True).data,
            status.HTTP_200_OK
        )


class OutgoingFriendRequestView(generics.ListCreateAPIView):
    """
    Исходящие заявки в друзья
    """
    queryset = FriendshipRequest.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = FriendshipRequestSerializer

    def get(self, request, *args, **kwargs):
        """
        Получить исходящие заявки в друзья для user
        """
        from_user = request.user
        if from_user.is_anonymous:
            return Response(
                {'message': "UNAUTHORIZED"},
                status.HTTP_401_UNAUTHORIZED
            )
        # получаем все заявки в друзья, в которых from_user = request.user
        outgoing_requests = FriendshipRequest.objects.filter(from_user=from_user)
        if not outgoing_requests:
            return Response(
                    {'message': "NOT FOUND"},
                    status.HTTP_404_NOT_FOUND
                )
        return Response(
            FriendshipRequestSerializer(outgoing_requests, many=True).data,
            status.HTTP_200_OK
        )