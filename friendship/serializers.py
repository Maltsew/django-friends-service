from rest_framework import serializers
from .models import User, FriendshipRequest, Friends
from django.contrib.auth import authenticate



class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username',)

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )
        user.save()
        return user


class FriendshipRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipRequest
        fields = ('id', 'from_user', 'to_user', 'request_status')


class FriendSerializer(serializers.Serializer):
    pass