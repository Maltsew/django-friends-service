from django.urls import path, include, re_path
from friendship.views import RegisterView
from rest_framework import routers
from .views import CreateFriendRequestView

router = routers.DefaultRouter()
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('friend-requests/<int:pk>', CreateFriendRequestView.as_view(), name='friend-request'),
    path('auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
