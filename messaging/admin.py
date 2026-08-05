from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    @admin.display(
        ordering="sender__username",
        description="Sender",
    )
    def sender_username(self, obj):
        return obj.sender.username if obj.sender else "Deleted User"

    @admin.display(
        ordering="receiver__username",
        description="Receiver",
    )
    def receiver_username(self, obj):
        return obj.receiver.username if obj.receiver else "Deleted User"

    readonly_fields = (
        "created_at",
        "updated_at",
        "read_at",
        "is_read",
    )

    list_display = (
        "sender_username",
        "receiver_username",
        "is_read",
        "created_at",
    )

    list_display_links = (
        "sender_username",
        "receiver_username",
    )

    search_fields = (
        "sender__username",
        "receiver__username",
        "message",
    )

    list_filter = ("is_read",)

    ordering = ("-created_at",)

    list_select_related = (
        "sender",
        "receiver",
    )

    autocomplete_fields = (
        "sender",
        "receiver",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    fieldsets = (
        (
            "Message Information",
            {
                "fields": (
                    "sender",
                    "receiver",
                    "message",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_read",
                    "read_at",
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
