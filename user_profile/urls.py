from rest_framework import routers

from user_profile.views import UserProfileViewSet, UserProfileFollowViewSet

router = routers.DefaultRouter()
router.register("user_profiles", UserProfileViewSet)
router.register("user_profile_follows", UserProfileFollowViewSet)

urlpatterns = router.urls

app_name = "user-profile"
