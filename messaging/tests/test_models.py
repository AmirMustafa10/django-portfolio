from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import Message

User = get_user_model()


class MessageModelTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
            first_name="Amir",
            last_name="Mustafa",
        )

        self.receiver = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Doe",
        )

    def test_valid_message_is_saved(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="Hello John!",
        )

        self.assertEqual(message.message, "Hello John!")
        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)

    def test_message_is_trimmed_on_save(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="   Hello John!   ",
        )

        self.assertEqual(message.message, "Hello John!")

    def test_empty_message_is_invalid(self):
        message = Message(
            sender=self.sender,
            receiver=self.receiver,
            message="   ",
        )

        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_sender_cannot_be_receiver(self):
        message = Message(
            sender=self.sender,
            receiver=self.sender,
            message="Hello myself!",
        )

        with self.assertRaises(ValidationError):
            message.full_clean()

    def test_is_read_true_sets_read_at_automatically(self):
        message = Message(
            sender=self.sender,
            receiver=self.receiver,
            message="Read message",
            is_read=True,
        )

        message.full_clean()

        self.assertIsNotNone(message.read_at)
        self.assertTrue(message.is_read)

    def test_is_read_false_clears_read_at(self):
        message = Message(
            sender=self.sender,
            receiver=self.receiver,
            message="Unread message",
            is_read=False,
            read_at=timezone.now(),
        )

        message.full_clean()

        self.assertIsNone(message.read_at)
        self.assertFalse(message.is_read)

    def test_mark_as_read_updates_is_read_and_read_at(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="Mark me as read",
        )

        message.mark_as_read()

        message.refresh_from_db()

        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)

    def test_str_returns_sender_receiver_and_message_preview(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="This is a very long message for preview testing.",
        )

        self.assertEqual(
            str(message),
            "amir → john: This is a very long ",
        )

    def test_deleted_sender_is_handled_in_str(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="Hello John!",
        )

        self.sender.delete()
        message.refresh_from_db()

        self.assertEqual(
            str(message),
            "Deleted User → john: Hello John!",
        )

    def test_deleted_receiver_is_handled_in_str(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            message="Hello John!",
        )

        self.receiver.delete()
        message.refresh_from_db()

        self.assertEqual(
            str(message),
            "amir → Deleted User: Hello John!",
        )

    def test_database_constraint_prevents_sender_equal_receiver(self):
        message = Message(
            sender=self.sender,
            receiver=self.sender,
            message="Hello myself!",
        )

        with self.assertRaises(ValidationError):
            message.save()

    def test_database_constraint_prevents_sender_equal_receiver_bulk_create(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Message.objects.bulk_create(
                    [
                        Message(
                            sender=self.sender,
                            receiver=self.sender,
                            message="Hello myself!",
                        )
                    ]
                )
