from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Skill


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
