from django.contrib import admin

from user.admin import CoreModelAdmin
from user_profile.models import UserProfile, UserProfileFollow


@admin.register(UserProfile)
class UserProfileAdmin(CoreModelAdmin):
    list_display = ("created_by", "bio", "created_at", "updated_at")
    search_fields = ("created_by__email",)
    ordering = ("created_by", "-updated_at",)


@admin.register(UserProfileFollow)
class UserProfileFollowAdmin(CoreModelAdmin):
    list_display = ("created_by", "following", "created_at", "updated_at")
    search_fields = ("created_by__email",)
    ordering = ("created_by", "-updated_at",)
