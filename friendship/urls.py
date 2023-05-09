from django.urls import path, include, re_path
from friendship.views import RegisterView
from rest_framework import routers
from .views import CreateFriendRequestView, AcceptFriendRequestView

router = routers.DefaultRouter()
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('friend-requests/<int:pk>', CreateFriendRequestView.as_view(), name='friend-request'),
    path('friend-requests/<int:pk>/accept', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
