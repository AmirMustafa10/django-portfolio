from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Skill, Project


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")

    list_display = (
        "name",
        "icon",
        "created_at",
    )

    list_display_links = ("name",)

    search_fields = ("name",)

    ordering = ("name",)

    list_per_page = 25


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    @admin.display(
        ordering="profile__user__username",
        description="owner",
    )
    def owner(self, obj):
        return obj.profile.user.username

    readonly_fields = ("slug", "owner", "created_at", "updated_at")

    list_display = (
        "title",
        "owner",
        "status",
        "is_featured",
        "created_at",
    )

    list_display_links = ("title",)

    search_fields = (
        "title",
        "profile__user__username",
    )

    list_filter = ("status", "is_featured")

    ordering = ("-created_at",)

    list_select_related = ("profile",)

    autocomplete_fields = (
        "profile",
        "skills",
    )

    date_hierarchy = "created_at"

    list_editable = (
        "status",
        "is_featured",
    )

    save_on_top = True

    filter_horizontal = ("skills",)

    list_per_page = 25

    fieldsets = (
        (
            "Project details",
            {
                "fields": (
                    "profile",
                    "title",
                    "description",
                    "status",
                    "created_at",
                    "is_featured",
                ),
            },
        ),
        (
            "Project skills",
            {
                "fields": ("skills",),
            },
        ),
        (
            "Project Links",
            {
                "fields": (
                    "live_demo_url",
                    "source_code_url",
                ),
            },
        ),
    )
