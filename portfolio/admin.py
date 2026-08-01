from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "icon",
    )

    list_display_links = ("name",)

    search_fields = ("name",)
    
    ordering = ("name",)
    
    list_per_page = 25

