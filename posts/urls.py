from rest_framework import routers

from posts.views import HashTagViewSet, LikeViewSet, CommentViewSet, PostViewSet

router = routers.DefaultRouter()
router.register("hash_tags", HashTagViewSet)
router.register("likes", LikeViewSet)
router.register("comments", CommentViewSet)
router.register("posts", PostViewSet)

urlpatterns = router.urls

app_name = "posts"
