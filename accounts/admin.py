from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    @admin.display(ordering="user__username", description="Username")
    def username(self, obj):
        return obj.user.username

    readonly_fields = ("created_at", "updated_at")

    list_display = (
        "username",
        "location",
        "available_for_work",
        "created_at",
    )

    list_display_links = ("username",)

    search_fields = (
        "user__username",
        "username",
        "location",
    )

    list_filter = ("available_for_work",)

    ordering = ("user__username",)

    list_select_related = ("user",)

    list_per_page = 25

    fieldsets = (
        (
            "User Identity",
            {
                "fields": (
                    "user",
                    "bio",
                    "location",
                    "available_for_work",
                ),
            },
        ),
        (
            "User Skills",
            {
                "fields": ("skills",),
            },
        ),
        (
            "Media & Documents",
            {
                "fields": (
                    "avatar",
                    "resume",
                ),
            },
        ),
        (
            "Social & Portfolio Links",
            {
                "classes": ("collapse",),  # Makes this section collapsible in admin
                "fields": (
                    "github_url",
                    "linkedin_url",
                    "website_url",
                ),
            },
        ),
        (
            "System Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )
