from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db import models
from core.models import TimeStampedModel, validate_file_size
from django.core.validators import FileExtensionValidator
from django.db.models import Max, UniqueConstraint
import os
from django.utils import timezone


def image_upload_path(instance, filename):
    """
    Upload path:
    images/YYYY/MM/DD/<username>_image.<ext>
    """
    _, extension = os.path.splitext(filename)
    today = timezone.now()

    return os.path.join(
        "images",
        today.strftime("%Y"),
        today.strftime("%m"),
        today.strftime("%d"),
        f"{instance.project.slug}_image{extension.lower()}",
    )


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


class Project(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="projects",
        on_delete=models.CASCADE,
    )

    skills = models.ManyToManyField(
        "portfolio.Skill",
        related_name="projects",
        blank=True,
    )

    title = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="Unique SEO-friendly slug generated automatically from the project title.",
    )

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
        db_index=True,
    )

    live_demo_url = models.URLField(
        blank=True,
        null=True,
    )

    source_code_url = models.URLField(
        blank=True,
        null=True,
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Highlight this project in featured sections.",
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"

        ordering = ("title",)

        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["title", "status"]),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(live_demo_url__isnull=False)
                    | models.Q(source_code_url__isnull=False)
                ),
                name="project_requires_at_least_one_link",
            ),
            models.UniqueConstraint(
                fields=["profile", "title"],
                name="unique_project_title_per_profile",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.status == self.Status.COMPLETED
            and not self.live_demo_url
            and not self.source_code_url
        ):
            raise ValidationError(
                {
                    "status": (
                        "A completed project must have at least one "
                        "link (Live Demo or Source Code)."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProjectImage(TimeStampedModel):
    project = models.ForeignKey(
        "Project", related_name="images", on_delete=models.CASCADE
    )

    image = models.ImageField(
        upload_to=image_upload_path,
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        ],
    )

    caption = models.CharField(
        max_length=150,
        blank=True,
    )

    display_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["project", "display_order"]

        constraints = [
            UniqueConstraint(
                fields=["project", "display_order"], name="unique_project_image_order"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.pk and self.display_order == 0:
            max_order = ProjectImage.objects.filter(project=self.project).aggregate(
                Max("display_order")
            )["display_order__max"]

            self.display_order = (max_order or 1) + 1

        super().save(*args, **kwargs)

    def __str__(self):
        if self.caption:
            return f"{self.project.title} - {self.caption}"

        return f"{self.project.title} - Image {self.display_order}"
