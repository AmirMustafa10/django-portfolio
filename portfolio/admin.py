from django.contrib import admin
from .models import Skill, Project, ProjectImage, Experience


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


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = (
        "image",
        "caption",
        "display_order",
    )
    ordering = ("display_order",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    readonly_fields = ("slug", "created_at", "updated_at")

    list_display = (
        "title",
        "profile",
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

    inlines = (ProjectImageInline,)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):

    readonly_fields = ("created_at", "updated_at")

    list_display = (
        "company_name",
        "job_title",
        "profile",
        "employment_type",
        "start_date",
        "end_date",
        "currently_working",
    )

    list_display_links = (
        "company_name",
        "job_title",
    )

    search_fields = (
        "company_name",
        "profile__user__username",
        "job_title",
    )

    list_filter = (
        "employment_type",
        "currently_working",
    )

    ordering = ("-start_date",)

    list_select_related = ("profile",)

    autocomplete_fields = ("profile",)

    date_hierarchy = "created_at"

    list_editable = (
        "employment_type",
        "currently_working",
    )

    save_on_top = True

    list_per_page = 25

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "profile",
                    "company_name",
                    "job_title",
                    "employment_type",
                )
            },
        ),
        (
            "Dates & Status",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "currently_working",
                )
            },
        ),
        (
            "Details",
            {
                "fields": ("description",),
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
