from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from core.models import Activity
from ..models import Message

User = get_user_model()


class MessagingViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.other_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
        )
        self.third_user = User.objects.create_user(
            username="sara",
            email="sara@example.com",
            password="StrongPass123!",
        )

        self.outgoing_message = Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            message="Hello John!",
            is_read=True,
        )

        self.incoming_unread_message = Message.objects.create(
            sender=self.other_user,
            receiver=self.user,
            message="Hello Amir!",
            is_read=False,
        )

        self.editable_message = Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            message="Original message.",
            is_read=False,
        )

        self.deletable_message = Message.objects.create(
            sender=self.user,
            receiver=self.other_user,
            message="Message to delete.",
            is_read=False,
        )

        self.other_conversation_message = Message.objects.create(
            sender=self.third_user,
            receiver=self.other_user,
            message="Another conversation.",
            is_read=False,
        )

    def message_data(self, **overrides):
        data = {
            "message": "Hello there!",
        }
        data.update(overrides)
        return data

    # -------------------------
    # messages view
    # -------------------------

    def test_messages_view_requires_login(self):
        response = self.client.get(reverse("messaging:messages"))

        expected = f"{reverse('accounts:login')}?next={reverse('messaging:messages')}"
        self.assertRedirects(response, expected)

    def test_messages_view_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("messaging:messages"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/messages.html")

    def test_messages_view_shows_only_conversation_users(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("messaging:messages"))

        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        usernames = [user.username for user in page_obj.object_list]

        self.assertIn("john", usernames)
        self.assertNotIn("sara", usernames)

    def test_messages_view_annotates_unread_count(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("messaging:messages"))

        page_obj = response.context["page_obj"]
        john = page_obj.object_list[0]

        self.assertEqual(john.username, "john")
        self.assertEqual(john.unread_count, 1)

    # -------------------------
    # conversation view
    # -------------------------

    def test_conversation_view_requires_login(self):
        response = self.client.get(
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            )
        )

        expected = (
            f"{reverse('accounts:login')}?"
            f"next={reverse('messaging:conversation', kwargs={'username': self.other_user.username})}"
        )
        self.assertRedirects(response, expected)

    def test_conversation_view_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "messaging/conversation.html")

    def test_conversation_view_cannot_open_self_conversation(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("messaging:conversation", kwargs={"username": self.user.username})
        )

        self.assertRedirects(response, reverse("messaging:messages"))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "You cannot send a message to yourself." in str(message)
                for message in messages
            )
        )

    def test_conversation_view_marks_incoming_unread_messages_as_read(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            )
        )

        self.assertEqual(response.status_code, 200)

        self.incoming_unread_message.refresh_from_db()
        self.assertTrue(self.incoming_unread_message.is_read)
        self.assertIsNotNone(self.incoming_unread_message.read_at)

    # -------------------------
    # send message view
    # -------------------------

    def test_send_message_view_requires_login(self):
        response = self.client.get(
            reverse(
                "messaging:send_message", kwargs={"username": self.other_user.username}
            )
        )

        expected = (
            f"{reverse('accounts:login')}?"
            f"next={reverse('messaging:send_message', kwargs={'username': self.other_user.username})}"
        )
        self.assertRedirects(response, expected)

    def test_send_message_view_get_redirects_to_conversation(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "messaging:send_message", kwargs={"username": self.other_user.username}
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            ),
        )

    def test_send_message_view_post_creates_message_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "messaging:send_message", kwargs={"username": self.other_user.username}
            ),
            data=self.message_data(message="Hello John!"),
        )

        self.assertRedirects(
            response,
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            ),
        )

        self.assertTrue(
            Message.objects.filter(
                sender=self.user,
                receiver=self.other_user,
                message="Hello John!",
            ).exists()
        )

        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_send_message_view_cannot_send_message_to_self(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("messaging:send_message", kwargs={"username": self.user.username})
        )

        self.assertRedirects(response, reverse("messaging:messages"))

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "You cannot send a message to yourself." in str(message)
                for message in messages
            )
        )

    # -------------------------
    # edit message view
    # -------------------------

    def test_edit_message_view_requires_login(self):
        response = self.client.get(
            reverse(
                "messaging:edit_message",
                kwargs={
                    "username": self.other_user.username,
                    "id": self.editable_message.id,
                },
            )
        )

        expected = (
            f"{reverse('accounts:login')}?"
            f"next={reverse('messaging:edit_message', kwargs={'username': self.other_user.username, 'id': self.editable_message.id})}"
        )
        self.assertRedirects(response, expected)

    def test_edit_message_view_owner_only(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                "messaging:edit_message",
                kwargs={
                    "username": self.other_user.username,
                    "id": self.editable_message.id,
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_message_view_post_updates_message_and_activity(self):
        self.client.force_login(self.user)

        referer = f"http://testserver{reverse('messaging:conversation', kwargs={'username': self.other_user.username})}?page=2"

        response = self.client.post(
            reverse(
                "messaging:edit_message",
                kwargs={
                    "username": self.other_user.username,
                    "id": self.editable_message.id,
                },
            ),
            data=self.message_data(message="Updated message."),
            HTTP_REFERER=referer,
        )

        self.assertRedirects(
            response,
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            )
            + "?page=2",
        )

        self.editable_message.refresh_from_db()
        self.assertEqual(self.editable_message.message, "Updated message.")

        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.UPDATED,
            ).exists()
        )

    def test_edit_message_view_post_invalid_data_redirects_back(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "messaging:edit_message",
                kwargs={
                    "username": self.other_user.username,
                    "id": self.editable_message.id,
                },
            ),
            data=self.message_data(message="   "),
        )

        self.assertRedirects(
            response,
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            ),
        )

    # -------------------------
    # delete message view
    # -------------------------

    def test_delete_message_view_requires_login(self):
        response = self.client.get(
            reverse(
                "messaging:delete_message", kwargs={"id": self.deletable_message.id}
            )
        )

        expected = (
            f"{reverse('accounts:login')}?"
            f"next={reverse('messaging:delete_message', kwargs={'id': self.deletable_message.id})}"
        )
        self.assertRedirects(response, expected)

    def test_delete_message_view_get_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "messaging:delete_message", kwargs={"id": self.deletable_message.id}
            )
        )

        self.assertEqual(response.status_code, 405)

    def test_delete_message_view_post_deletes_message_and_activity(self):
        self.client.force_login(self.user)

        referer = f"http://testserver{reverse('messaging:conversation', kwargs={'username': self.other_user.username})}"

        response = self.client.post(
            reverse(
                "messaging:delete_message", kwargs={"id": self.deletable_message.id}
            ),
            HTTP_REFERER=referer,
        )

        self.assertRedirects(
            response,
            reverse(
                "messaging:conversation", kwargs={"username": self.other_user.username}
            ),
        )
        self.assertFalse(Message.objects.filter(pk=self.deletable_message.pk).exists())

        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.DELETED,
            ).exists()
        )

    def test_delete_message_view_owner_only(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                "messaging:delete_message", kwargs={"id": self.deletable_message.id}
            )
        )

        self.assertEqual(response.status_code, 404)
