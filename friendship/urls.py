from django.urls import path, include, re_path
from friendship.views import RegisterView
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('friend-requests/<int:pk>/', CreateFriendRequestView.as_view(), name='friend-request'),
    path('friend-requests/<int:pk>/accept/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('friend-requests/<int:pk>/reject/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('friend-requests/incoming/', IncomingFriendRequestView.as_view(), name='friend-request-incoming'),
    path('friend-requests/outgoing/', OutgoingFriendRequestView.as_view(), name='friend-request-outgoing'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('friendship-status/', FriendshipStatusListView.as_view(), name='friendship-status'),
    path('friends/<int:pk>/', RemoveFromFriendView.as_view(), name='remove-friend'),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
