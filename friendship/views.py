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
from .serializers import RegisterSerializer, FriendshipRequestSerializer, FriendSerializer
from rest_framework import generics
from rest_framework.views import APIView
from django.core import serializers

from django.http import JsonResponse



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
            FriendshipRequest.objects.filter(pk=kwargs['pk']).update(request_status=3)
            try:
                # если заявка принята - создаем дружбу
                friendships = Friends.objects.create(from_user=friend_request.from_user, to_user=to_user)
                # если создалась дружба - удаляем заявку на дружбу
                accepted_request = FriendshipRequest.objects.get(pk=kwargs['pk'])
                accepted_request.delete()
            # если уже друзья - обрабатываем как 400
            except (IntegrityError, UniqueViolation) as e:
                return Response(
                    {'message': str(e)},
                    status.HTTP_400_BAD_REQUEST
                )
            return Response(
                FriendshipRequestSerializer(friendships).data,
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


class FriendListView(generics.ListCreateAPIView):
    """
    Просмотр списка своих друзей
    Создать дружбу между user1 и user2 можно 2 способами:
    1) user1 отправил заявку в друзья user2, и user2 ее принял
    2) user2 отправил заявку в друзья user1, и user 1 ее принял
    Дружба является взаимной, то есть в конкретном примере не важно,
    является ли request.user from_user либо to_user
    """
    serializer_class = FriendSerializer

    def get(self, request, *args, **kwargs):
        """
        Получить список своих друзей
        """
        user = request.user
        if user.is_anonymous:
            return Response(
                {'message': "UNAUTHORIZED"},
                status.HTTP_401_UNAUTHORIZED
            )
        # получаем все отношения Friends, где user либо в to_user, либо в from_user
        friends_1 = Friends.objects.filter(from_user=user)
        friends_2 = Friends.objects.filter(to_user=user)
        # если user нет ни в одном сете, то есть нет дружбы ни в каком отношнении
        if not friends_1 and not friends_2:
            return Response(
                {'message': "NOT FOUND"},
                status.HTTP_404_NOT_FOUND
            )
        friend_list = {}
        # придумал бы логику получше, но очень спешил:
        # из двух qs, где request.user либо в to_user, либо в from_user
        # собираю один словарь, в который кладу id и username друга
        for user in friends_1:
            user_id = user.to_user_id
            username = user.to_user.username
            friend_list[user_id] = username
        for user in friends_2:
            user_id = user.from_user_id
            username = user.from_user.username
            friend_list[user_id] = username
        # и вывожу пары id: username json-ом
        return JsonResponse(friend_list)

class FriendshipStatusListView(generics.ListCreateAPIView):
    users = User.objects.all()
    friend_request_queryset = FriendshipRequest.objects.all()
    friendship_queryset = Friends.objects.all()
    serializer_class = FriendSerializer
    """
    Статус дружбы пользователя с другим пользователем
    """
    def get(self, request, *args, **kwargs):
        """
        Получить статус дружбы
        """
        user = request.user
        if user.is_anonymous:
            return Response(
                {'message': "UNAUTHORIZED"},
                status.HTTP_401_UNAUTHORIZED
            )
        user_id = request.user.id # сам user
        checked_user_id = request.GET.get('user_id') # id пользователя, с которым проверяется статус дружбы
        user_username = FriendshipStatusListView.users.get(id=user_id)
        checked_user_username = FriendshipStatusListView.users.get(id=checked_user_id)
        # необходимо сделать две проверки на наличие любых отношений в Friends
        first_friendship_check = FriendshipStatusListView.friendship_queryset.filter(from_user=user_username,
                                                                                     to_user=checked_user_username)
        second_friendship_check = FriendshipStatusListView.friendship_queryset.filter(from_user=checked_user_username,
                                                                                     to_user=user_username)
        if first_friendship_check or second_friendship_check:
            return Response(
                {'message': "Уже друзья"},
                status.HTTP_200_OK
                )
        first_friend_request_check = FriendshipStatusListView.friend_request_queryset.filter(from_user=user_username,
                                                                                     to_user=checked_user_username)
        if first_friend_request_check:
            return Response(
                {'message': "Есть исходящая заявка к этому пользователю"},
                status.HTTP_200_OK
            )
        second_friend_request_check = FriendshipStatusListView.friend_request_queryset.filter(from_user=checked_user_username,
                                                                                             to_user=user_username)
        if first_friend_request_check:
            return Response(
                {'message': "Есть входящая заявка от этого пользователя"},
                status.HTTP_200_OK
            )
        return Response(
            {'message': "Нет ничего"},
            status.HTTP_200_OK
        )