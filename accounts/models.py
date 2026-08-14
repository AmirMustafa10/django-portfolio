import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel, validate_file_size
from django.db.models.functions import Lower


def avatar_upload_path(instance, filename):
    """
    Upload path:
    avatars/YYYY/MM/DD/<username>.<ext>
    """
    _, extension = os.path.splitext(filename)
    today = timezone.now()

    username = instance.user.username if instance.user_id else "user"

    return os.path.join(
        "avatars",
        today.strftime("%Y"),
        today.strftime("%m"),
        today.strftime("%d"),
        f"{username}{extension.lower()}",
    )


def resume_upload_path(instance, filename):
    """
    Upload path:
    resumes/YYYY/MM/DD/<username>_resume.pdf
    """
    _, extension = os.path.splitext(filename)
    today = timezone.now()

    username = instance.user.username if instance.user_id else "user"

    return os.path.join(
        "resumes",
        today.strftime("%Y"),
        today.strftime("%m"),
        today.strftime("%d"),
        f"{username}_resume{extension.lower()}",
    )


username_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_.-]+$",
    message=(
        "Username may contain only letters, numbers, " "dots, underscores, and hyphens."
    ),
)


class User(AbstractUser):
    """Custom user model."""

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("username"),
                name="unique_username_case_insensitive",
            ),
            models.UniqueConstraint(
                Lower("email"),
                name="unique_email_case_insensitive",
            ),
        ]

    def clean(self):
        super().clean()

        if self.username:
            if (
                type(self)
                .objects.filter(username__iexact=self.username)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    {"username": ("A user with this username already exists.")}
                )

        if self.email:
            if (
                type(self)
                .objects.filter(email__iexact=self.email)
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    {"email": ("A user with this email already exists.")}
                )


class Profile(TimeStampedModel):

    jop_title = models.CharField(max_length=50)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    skills = models.ManyToManyField(
        "portfolio.Skill", related_name="profiles", blank=True
    )

    bio = models.TextField(max_length=150)

    about = models.TextField()

    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
        ],
    )

    resume = models.FileField(
        upload_to=resume_upload_path,
        blank=True,
        null=True,
        validators=[
            validate_file_size,
            FileExtensionValidator(allowed_extensions=["pdf"]),
        ],
    )

    github_url = models.URLField(max_length=300, blank=True, null=True)

    linkedin_url = models.URLField(max_length=300, blank=True, null=True)

    website_url = models.URLField(max_length=300, blank=True, null=True)

    location = models.CharField(max_length=250, blank=True, null=True)

    available_for_work = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ("user__username",)
        indexes = [
            models.Index(
                fields=["available_for_work"],
                name="available_for_work_idx",
            ),
            models.Index(
                fields=["location"],
                name="profile_location_idx",
            ),
        ]

    def clean(self):
        super().clean()

        links = (
            self.github_url,
            self.linkedin_url,
            self.website_url,
        )

        if self.available_for_work and not any(links):
            raise ValidationError(
                "At least one professional link (GitHub, LinkedIn, or Website) is required when the profile is marked as available for work."
            )

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"
