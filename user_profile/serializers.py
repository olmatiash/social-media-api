from rest_framework import serializers

from user.serializers import CoreModelSerializer
from user_profile.models import UserProfile, UserProfileFollow


class UserProfileFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileFollow
        fields = ("id", "created_by", "following")
        read_only_fields = ("created_by",)


class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "image")


class UserProfileSerializer(CoreModelSerializer, serializers.ModelSerializer):
    followings = serializers.SerializerMethodField(read_only=True)
    followers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "bio",
            "image",
            "followers",
            "followings",
        ) + CoreModelSerializer.Meta.fields

    def get_followings(self, obj):
        qs = UserProfileFollow.objects.filter(created_by=obj.created_by)
        return [follow.following_id for follow in qs]

    def get_followers(self, obj):
        qs = UserProfileFollow.objects.filter(following=obj.created_by)
        return [follow.created_by_id for follow in qs]


class UserProfileListSerializer(UserProfileSerializer):
    followers_count = serializers.IntegerField(read_only=True)
    followings_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "bio",
            "image",
            "followers_count",
            "followings_count",
            "posts_count",
        ) + CoreModelSerializer.Meta.fields


class UserProfileDetailSerializer(UserProfileSerializer):
    posts = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = UserProfileSerializer.Meta.fields + ("posts", "followings")
