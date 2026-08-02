from django.db import models
from core.models import TimeStampedModel


class Skill(TimeStampedModel):
    name = models.CharField(
        max_length=100,
        unique=True,
    )

    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="CSS class for the icon.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
