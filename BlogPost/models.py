from django.db import models
from core.models import TimeStampedModel, validate_file_size
import os
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


def image_upload_path(instance, filename):
    """
    Upload path:
    images/Blog/YYYY/MM/DD/<username>_blog_image.<ext>
    """
    _, extension = os.path.splitext(filename)
    today = timezone.now()

    return os.path.join(
        "images",
        "Blog",
        today.strftime("%Y"),
        today.strftime("%m"),
        today.strftime("%d"),
        f"{instance.slug}_blog_image{extension.lower()}",
    )


class BlogPost(TimeStampedModel):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    profile = models.ForeignKey(
        "accounts.Profile",
        related_name="blog_posts",
        on_delete=models.CASCADE,
    )

    title = models.CharField(
        max_length=255,
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
    )

    content = models.TextField()

    cover_image = models.ImageField(
        upload_to=image_upload_path,
        validators=[
            validate_file_size,
            FileExtensionValidator(
                allowed_extensions=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ]
            ),
        ],
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

        ordering = ("-created_at",)

        indexes = [
            models.Index(
                fields=["status", "published_at"],
                name="blog_status_pub_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        status="published",
                        published_at__isnull=False,
                    )
                    | models.Q(
                        status="draft",
                        published_at__isnull=True,
                    )
                ),
                name="blog_status_published_at_consistency",
            ),
        ]

    def clean(self):
        super().clean()

        if self.status == self.Status.PUBLISHED:
            if self.published_at is None:
                self.published_at = timezone.now()

        elif self.status == self.Status.DRAFT:
            self.published_at = None

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):

    blog_post = models.ForeignKey(
        "BlogPost",
        related_name="comments",
        on_delete=models.CASCADE,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    content = models.TextField(
        max_length=500,
        db_index=False,
    )

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

        ordering = ("-created_at",)

        indexes = [
            models.Index(
                fields=["blog_post", "-created_at"],
                name="comment_post_created_idx",
            )
        ]

    def clean(self):
        super().clean()

        if self.content:
            self.content = self.content.strip()

        if not self.content:
            raise ValidationError({"content": "Comment cannot be empty."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        username = self.user.username if self.user else "Deleted User"

        return f"comment {username} - {self.blog_post.title}"
