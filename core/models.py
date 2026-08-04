from django.db import models
from django.core.exceptions import ValidationError

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
