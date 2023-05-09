from django.contrib import admin
from .models import User, FriendshipRequest, Friends
from django.contrib import auth


admin.site.unregister(auth.models.Group)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username',)
    search_fields = ('title',)


class FriendshipRequestAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user',)


class FriendsAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user',)


admin.site.register(User, UserAdmin)
admin.site.register(FriendshipRequest, FriendshipRequestAdmin)
admin.site.register(Friends, FriendsAdmin)