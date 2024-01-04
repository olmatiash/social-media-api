import pytz
from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.response import Response
from django.db.models import Count, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from social_media_api.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from posts.tasks import post_schedule_create
from user.views import CoreModelMixin
from user_profile.models import UserProfile
from posts.models import HashTag, Like, Comment, Post
from posts.serializers import (
    HashTagSerializer,
    LikeSerializer,
    CommentSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostImageSerializer,
    CommentDetailSerializer,
)


class HashTagViewSet(viewsets.ModelViewSet):
    queryset = HashTag.objects.all()
    serializer_class = HashTagSerializer


class LikeViewSet(CoreModelMixin, viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]


class CommentViewSet(CoreModelMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [
        IsOwnerOrReadOnly,
    ]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CommentDetailSerializer

        return CommentSerializer


class PostPagination(PageNumberPagination):
    page_size = 3
    max_page_size = 100


class PostViewSet(CoreModelMixin, viewsets.ModelViewSet):
    queryset = Post.objects.all()
    pagination_class = PostPagination
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = self.queryset.annotate(
            likes_count=(Count("likes", distinct=True)),
            comments_count=(Count("comments", distinct=True)),
        )

        if self.action != "create":
            queryset.select_related("likes", "comments").prefetch_related(
                "hashtags"
            )

        queryset = self.filter_queryset(queryset)
        return queryset

    def filter_queryset(self, queryset):
        for param_name in ["email", "first_name", "last_name", "username"]:
            param = self.request.query_params.get(param_name)

            if param:
                queryset = queryset.filter(
                    **{f"created_by__{param_name}__icontains": param}
                )

        hashtags = self.request.query_params.get("hashtags")
        title = self.request.query_params.get("title")
        profile = self.request.query_params.get("profile")
        liked = self.request.query_params.get("liked")

        if hashtags:
            hashtags_ids = [int(str_id) for str_id in hashtags.split(",")]
            queryset = queryset.filter(hashtags__id__in=hashtags_ids)

        if title:
            queryset = queryset.filter(title__icontains=title)

        if profile:
            queryset = queryset.filter(profile=profile)

        if liked:
            queryset = queryset.filter(likes__created_by=self.request.user)

        queryset = queryset.filter(
            Q(is_visible=True) | Q(created_by=self.request.user)
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action == "upload_image":
            return PostImageSerializer

        return PostSerializer

    def perform_create(self, serializer, *args, **kwargs):
        user_profile = UserProfile.objects.get(
            created_by_id=self.request.user.pk
        )
        post = super().perform_create(serializer, profile=user_profile)

        scheduled_time = post.scheduled_time

        if scheduled_time:
            timezone = pytz.timezone("Europe/Kiev")
            now = datetime.now().astimezone(timezone)

            if scheduled_time < now:
                raise ValidationError("Incorrect scheduled time.")

            if post.is_visible:
                raise ValidationError(
                    "Scheduled time is not applicable if post is visible."
                )

            post_schedule_create.apply_async(
                args=[post.id], eta=scheduled_time
            )

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[
            IsAuthenticated,
            IsOwnerOnly,
        ],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific user profile"""
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                description="Filter by email (ex. ?email=example@gmail.com)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="first_name",
                description="Filter by first name (ex. ?first_name=John)",
                required=False,
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter by last name (ex. ?last_name=Smith)",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="username",
                description="Filter by username (ex. ?username=mate)",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="title",
                description="Filter by title (ex. ?title=Develop)",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="profile",
                description="Filter by profile id (ex. ?profile=2)",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="hashtags",
                description="Filter by hashtag ids (ex. ?hashtags=1,2)",
                type={"type": "list", "items": {"type": "number"}},
            ),
            OpenApiParameter(
                name="liked",
                description="Filter liked posts (ex. ?liked=True)",
                type=OpenApiTypes.BOOL,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
