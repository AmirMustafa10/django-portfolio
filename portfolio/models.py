from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db import models
from core.models import TimeStampedModel, validate_file_size
from django.core.validators import FileExtensionValidator
from django.db.models import Max, UniqueConstraint, F
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
        verbose_name = "image"
        verbose_name_plural = "images"
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


class Experience(TimeStampedModel):

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"
        FREELANCE = "freelance", "Freelance"

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="experiences",
        on_delete=models.CASCADE,
    )

    company_name = models.CharField(
        max_length=250,
    )

    job_title = models.CharField(
        max_length=250,
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
    )

    description = models.TextField(
        blank=True,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    currently_working = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"

        ordering = ("-start_date",)

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        currently_working=True,
                        end_date__isnull=True,
                    )
                    | models.Q(
                        currently_working=False,
                    )
                ),
                name="experience_currently_working_no_end_date",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(end_date__isnull=True)
                    | models.Q(start_date__lte=F("end_date"))
                ),
                name="experience_start_before_end",
            ),
        ]

    def clean(self):
        super().clean()

        if self.currently_working and self.end_date:
            raise ValidationError(
                {"end_date": ("End date must be empty while currently working.")}
            )

        if not self.currently_working and not self.end_date:
            raise ValidationError(
                {"end_date": ("End date is required when you are no longer working.")}
            )

        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": ("End date cannot be earlier than start date.")}
            )

    def __str__(self):
        return f"{self.company_name} - {self.job_title}"


class Education(TimeStampedModel):

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="educations",
        on_delete=models.CASCADE,
    )

    institution = models.CharField(max_length=255)

    degree = models.CharField(max_length=255)

    field_of_study = models.CharField(
        max_length=255,
        blank=True,
    )

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    grade = models.CharField(
        max_length=100,
        blank=True,
    )

    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Educations"

        ordering = ("-start_date",)

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(end_date__isnull=True)
                    | models.Q(start_date__lte=F("end_date"))
                ),
                name="education_start_before_end",
            ),
        ]

    def clean(self):
        super().clean()

        if self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                {"end_date": ("End date cannot be earlier than start date.")}
            )

    def __str__(self):
        return f"{self.institution} - {self.degree}"
