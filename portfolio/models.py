from django.core.exceptions import ValidationError
from django.utils.text import slugify
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
