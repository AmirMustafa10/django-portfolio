from django.contrib import admin
from .models import BlogPost, Comment


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    @admin.display(
        ordering="user__username",
        description="Author",
    )
    def author(self, obj):
        return obj.user.username if obj.user else "Deleted User"

    @admin.display(
        ordering="blog_post__title",
        description="Blog Post",
    )
    def post_title(self, obj):
        return obj.blog_post.title

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_display = (
        "author",
        "post_title",
        "created_at",
    )

    list_display_links = (
        "author",
        "post_title",
    )

    search_fields = (
        "user__username",
        "blog_post__title",
        "content",
    )

    list_select_related = (
        "user",
        "blog_post",
    )

    autocomplete_fields = (
        "user",
        "blog_post",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    list_per_page = 25

    fieldsets = (
        (
            "Comment Information",
            {
                "fields": (
                    "user",
                    "parent",
                    "blog_post",
                    "content",
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
