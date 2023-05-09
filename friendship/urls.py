from django.urls import path, include
from friendship.views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]
