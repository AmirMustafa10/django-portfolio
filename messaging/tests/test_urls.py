from django.test import SimpleTestCase
from django.urls import resolve, reverse
from messaging import views


class MessagingUrlsTest(SimpleTestCase):

    def test_messages_url_resolves(self):
        url = reverse("messaging:messages")
        self.assertEqual(resolve(url).func, views.messages_view)

    def test_conversation_url_resolves(self):
        url = reverse("messaging:conversation", kwargs={"username": "amir"})
        self.assertEqual(resolve(url).func, views.conversation_view)

    def test_send_message_url_resolves(self):
        url = reverse("messaging:send_message", kwargs={"username": "amir"})
        self.assertEqual(resolve(url).func, views.send_message_view)

    def test_edit_message_url_resolves(self):
        url = reverse(
            "messaging:edit_message",
            kwargs={"username": "amir", "id": 1},
        )
        self.assertEqual(resolve(url).func, views.edit_message_view)

    def test_delete_message_url_resolves(self):
        url = reverse("messaging:delete_message", kwargs={"id": 1})
        self.assertEqual(resolve(url).func, views.delete_message_view)
