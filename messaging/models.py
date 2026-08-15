from django.db import models
from core.models import TimeStampedModel
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone


class Message(TimeStampedModel):

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_messages",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    message = models.TextField(max_length=500)

    is_read = models.BooleanField(default=False)

    read_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

        ordering = ("-created_at",)

        get_latest_by = "created_at"

        indexes = [
            models.Index(
                fields=["sender"],
                name="message_sender_idx",
            ),
            models.Index(
                fields=["receiver", "is_read"],
                name="message_receiver_read_idx",
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=~models.Q(sender=models.F("receiver")),
                name="sender_cannot_be_receiver",
            )
        ]

    def clean(self) -> None:
        super().clean()

        if (
            self.sender is not None
            and self.receiver is not None
            and self.sender == self.receiver
        ):
            raise ValidationError(
                {"receiver": "You cannot send a message to yourself."}
            )

        if self.message:
            self.message = self.message.strip()

        if not self.message:
            raise ValidationError({"message": "Message cannot be empty."})

        if self.is_read and not self.read_at:
            self.read_at = timezone.now()

        if not self.is_read:
            self.read_at = None

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        sender = self.sender.username if self.sender else "Deleted User"
        receiver = self.receiver.username if self.receiver else "Deleted User"

        return f"{sender} → {receiver}: {self.message[:20]}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
