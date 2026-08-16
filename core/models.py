from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB


def validate_file_size(file):
    """Validate uploaded file size (max 2 MB)."""
    if file.size > MAX_FILE_SIZE:
        raise ValidationError("Maximum allowed file size is 2 MB.")


class TimeStampedModel(models.Model):
    """An abstract base class model that provides self-updating created_at and updated_at fields."""

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Activity(TimeStampedModel):

    class Action(models.TextChoices):
        CREATED = "created", "Created"
        UPDATED = "updated", "Updated"
        PUBLISHED = "published", "Published"
        DELETED = "deleted", "Deleted"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="activities",
        on_delete=models.CASCADE,
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices,
    )

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )

    target_object_id = models.PositiveBigIntegerField()

    target = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )

    class Meta:
        verbose_name = "Activity"
        verbose_name_plural = "Activities"
        ordering = ("-created_at",)

        indexes = [
            models.Index(
                fields=["user", "-created_at"],
                name="activity_user_created_idx",
            ),
            models.Index(
                fields=["target_content_type", "target_object_id"],
                name="activity_target_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action}"
