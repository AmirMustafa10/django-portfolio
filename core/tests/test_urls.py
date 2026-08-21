from django.test import SimpleTestCase
from django.urls import resolve, reverse
from core import views

class CoreUrlsTest(SimpleTestCase):

    def test_home_url_resolves(self):
        url = reverse("home")
        self.assertEqual(resolve(url).func, views.home)

    def test_dashboard_url_resolves(self):
        url = reverse("dashboard")
        self.assertEqual(resolve(url).func, views.dashboard_view)

    def test_activity_url_resolves(self):
        url = reverse("activity")
        self.assertEqual(resolve(url).func, views.activity_view)
