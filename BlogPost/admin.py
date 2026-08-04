from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):

    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
        "published_at",
    )

    list_display = (
        "title",
        "profile",
        "status",
        "published_at",
        "created_at",
    )

    list_display_links = ("title",)

    search_fields = (
        "title",
        "slug",
        "profile__user__username",
    )

    list_editable = ("status",)

    list_filter = ("status",)

    ordering = ("-created_at",)

    list_select_related = ("profile",)

    autocomplete_fields = ("profile",)

    date_hierarchy = "created_at"

    save_on_top = True

    list_per_page = 25

    fieldsets = (
        (
            "Post Information",
            {
                "fields": (
                    "profile",
                    "title",
                    "slug",
                    "content",
                    "cover_image",
                ),
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "published_at",
                ),
            },
        ),
        (
            "Metadata",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
