from django.test import SimpleTestCase
from django.urls import resolve, reverse

from accounts import views


class AccountsUrlsTest(SimpleTestCase):

    def test_register_url_resolves(self):
        url = reverse("accounts:register")
        self.assertEqual(resolve(url).func, views.register_view)

    def test_login_url_resolves(self):
        url = reverse("accounts:login")
        self.assertEqual(resolve(url).func, views.login_view)

    def test_logout_url_resolves(self):
        url = reverse("accounts:logout")
        self.assertEqual(resolve(url).func, views.logout_view)

    def test_developers_url_resolves(self):
        url = reverse("accounts:developers")
        self.assertEqual(resolve(url).func, views.developers_view)

    def test_developer_detail_url_resolves(self):
        url = reverse("accounts:developer_detail", kwargs={"username": "amir"})
        self.assertEqual(resolve(url).func, views.developer_detail_view)

    def test_create_profile_url_resolves(self):
        url = reverse("accounts:create_profile")
        self.assertEqual(resolve(url).func, views.create_profile_view)

    def test_edit_profile_url_resolves(self):
        url = reverse("accounts:edit_profile")
        self.assertEqual(resolve(url).func, views.edit_profile_view)
