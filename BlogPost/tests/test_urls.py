from django.test import SimpleTestCase
from django.urls import resolve, reverse

from BlogPost import views


class BlogUrlsTest(SimpleTestCase):

    def test_blogs_url_resolves(self):
        url = reverse("blog:blogs")
        self.assertEqual(resolve(url).func, views.blogpost_view)

    def test_blog_details_url_resolves(self):
        url = reverse("blog:blog_details", kwargs={"slug": "devconnect"})
        self.assertEqual(resolve(url).func, views.blogpost_details_view)

    def test_add_comment_url_resolves(self):
        url = reverse("blog:add_comment", kwargs={"blog_slug": "devconnect"})
        self.assertEqual(resolve(url).func, views.add_comment_view)

    def test_edit_comment_url_resolves(self):
        url = reverse(
            "blog:edit_comment",
            kwargs={"blog_slug": "devconnect", "comment_id": 1},
        )
        self.assertEqual(resolve(url).func, views.edit_comment_view)

    def test_delete_comment_url_resolves(self):
        url = reverse("blog:delete_comment", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.delete_comment_view)

    def test_my_blogs_url_resolves(self):
        url = reverse("blog:my_blogs")
        self.assertEqual(resolve(url).func, views.my_blogs_view)

    def test_add_blog_url_resolves(self):
        url = reverse("blog:add_blog")
        self.assertEqual(resolve(url).func, views.add_blog_view)

    def test_edit_blog_url_resolves(self):
        url = reverse("blog:edit_blog", kwargs={"blog_slug": "devconnect"})
        self.assertEqual(resolve(url).func, views.edit_blog_view)

    def test_delete_blog_url_resolves(self):
        url = reverse("blog:delete_blog", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func, views.delete_blog_view)
