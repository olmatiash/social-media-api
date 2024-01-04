import os
import uuid

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from user.models import CoreModel


def get_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.created_by)}-{uuid.uuid4()}{extension}"
    dirname = f"{slugify(type(instance).__name__)}s"

    return os.path.join("uploads", dirname, filename)


class UserProfile(CoreModel):
    bio = models.TextField()
    image = models.ImageField(
        blank=True, null=True, upload_to=get_image_file_path
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["created_by"], name="unique_created_by"
            )
        ]

    def __str__(self):
        return f"{self.id}: {self.created_by}"


class UserProfileFollow(CoreModel):
    following = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.CASCADE,
        related_name="followers",
    )
    created_by = models.ForeignKey(
        to=get_user_model(),
        editable=False,
        on_delete=models.CASCADE,
        related_name="followings",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["created_by", "following"], name="unique_follows"
            )
        ]

    def validate_following(self):
        if self.created_by == self.following:
            raise ValidationError("Cannot follow/unfollow your own profile.")

    def save(self, *args, **kwargs):
        self.validate_following()
        super(UserProfileFollow, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.created_by} follows {self.following}"
