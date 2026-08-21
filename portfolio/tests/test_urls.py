from django.test import SimpleTestCase
from django.urls import resolve, reverse
from portfolio import views


class PortfolioUrlsTest(SimpleTestCase):

    # -------------------------
    # Experience URLs
    # -------------------------

    def test_delete_experience_url_resolves(self):
        url = reverse("portfolio:delete_experience", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.delete_experience_view)

    def test_edit_experience_url_resolves(self):
        url = reverse("portfolio:edit_experience", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.edit_experience_view)

    def test_add_experience_url_resolves(self):
        url = reverse("portfolio:add_experience")
        self.assertEqual(resolve(url).func, views.add_experience_view)

    # -------------------------
    # Education URLs
    # -------------------------

    def test_delete_education_url_resolves(self):
        url = reverse("portfolio:delete_education", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.delete_education_view)

    def test_edit_education_url_resolves(self):
        url = reverse("portfolio:edit_education", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.edit_education_view)

    def test_add_education_url_resolves(self):
        url = reverse("portfolio:add_education")
        self.assertEqual(resolve(url).func, views.add_education_view)

    # -------------------------
    # Project URLs
    # -------------------------

    def test_projects_url_resolves(self):
        url = reverse("portfolio:projects")
        self.assertEqual(resolve(url).func, views.projects_view)

    def test_project_details_url_resolves(self):
        url = reverse("portfolio:project_details", kwargs={"slug": "devconnect"})
        self.assertEqual(resolve(url).func, views.project_details)

    def test_my_projects_url_resolves(self):
        url = reverse("portfolio:my_projects")
        self.assertEqual(resolve(url).func, views.my_projects_view)

    def test_add_project_url_resolves(self):
        url = reverse("portfolio:add_project")
        self.assertEqual(resolve(url).func, views.add_project_view)

    def test_edit_project_url_resolves(self):
        url = reverse("portfolio:edit_project", kwargs={"slug": "devconnect"})
        self.assertEqual(resolve(url).func, views.edit_project_view)

    def test_delete_project_url_resolves(self):
        url = reverse("portfolio:delete_project", kwargs={"slug": "devconnect"})
        self.assertEqual(resolve(url).func, views.delete_project_view)

    # -------------------------
    # Project Image URLs
    # -------------------------

    def test_manage_project_images_url_resolves(self):
        url = reverse(
            "portfolio:manage_project_images",
            kwargs={"slug": "devconnect"},
        )
        self.assertEqual(resolve(url).func, views.manage_project_images_view)

    def test_delete_project_image_url_resolves(self):
        url = reverse("portfolio:delete_project_image", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.delete_project_image_view)

    def test_edit_project_image_caption_url_resolves(self):
        url = reverse("portfolio:edit_project_image_caption", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.edit_project_image_caption_view)
