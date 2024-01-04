from rest_framework import serializers

from posts.models import HashTag, Like, Comment, Post
from user.serializers import CoreModelSerializer


class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ("id", "name")


class LikeSerializer(CoreModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "post", "created_by")


class CommentSerializer(CoreModelSerializer, serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ("id", "post", "content") + CoreModelSerializer.Meta.fields


class CommentDetailSerializer(
    CoreModelSerializer, serializers.ModelSerializer
):
    post = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "content", "post") + CoreModelSerializer.Meta.fields


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")


class PostSerializer(CoreModelSerializer, serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "hashtags",
            "content",
            "image",
            "profile",
            "is_visible",
            "scheduled_time",
        ) + CoreModelSerializer.Meta.fields

        read_only_fields = ("profile",)


class PostListSerializer(PostSerializer):
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = PostSerializer.Meta.fields + (
            "likes_count",
            "comments_count",
        )


class PostDetailSerializer(PostSerializer):
    likes = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="created_by_id"
    )
    comments = serializers.StringRelatedField(many=True, read_only=True)
    hashtags = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Post
        fields = PostSerializer.Meta.fields + (
            "likes",
            "comments",
        )
