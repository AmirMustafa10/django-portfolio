from django.contrib.auth import get_user_model
from django.test import TestCase
from ..forms import MessageForm
from ..models import Message

User = get_user_model()


class MessageFormTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.receiver = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
        )

    def test_valid_message_form(self):
        form = MessageForm(
            data={
                "message": "Hello John!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_empty_message_form_is_invalid(self):
        form = MessageForm(
            data={
                "message": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)

    def test_message_form_strips_whitespace(self):
        form = MessageForm(
            data={
                "message": "   Hello John!   ",
            }
        )

        self.assertTrue(form.is_valid())

        message = form.save(commit=False)
        message.sender = self.sender
        message.receiver = self.receiver
        message.save()

        self.assertEqual(message.message, "Hello John!")

    def test_message_form_saves_message(self):
        form = MessageForm(
            data={
                "message": "Hello John!",
            }
        )

        self.assertTrue(form.is_valid())

        message = form.save(commit=False)
        message.sender = self.sender
        message.receiver = self.receiver
        message.save()

        self.assertTrue(
            Message.objects.filter(
                sender=self.sender,
                receiver=self.receiver,
                message="Hello John!",
            ).exists()
        )

    def test_message_form_does_not_allow_blank_spaces_only(self):
        form = MessageForm(
            data={
                "message": "     ",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("message", form.errors)
