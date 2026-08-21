from io import BytesIO
from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from accounts.models import Profile
from core.models import Activity
from ..models import BlogPost, Comment

User = get_user_model()


def build_image_file(name="test.jpg", image_format="JPEG", color="blue"):
    image = Image.new("RGB", (100, 100), color=color)
    buffer = BytesIO()
    image.save(buffer, format=image_format)

    content_type = (
        "image/jpeg"
        if image_format.upper() in {"JPG", "JPEG"}
        else f"image/{image_format.lower()}"
    )

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type=content_type,
    )


class BlogViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
            first_name="Amir",
            last_name="Mustafa",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            jop_title="Backend Developer",
            bio="Short bio about Amir.",
            about="About Amir.",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

        self.other_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
            first_name="John",
            last_name="Doe",
        )
        self.other_profile = Profile.objects.create(
            user=self.other_user,
            jop_title="Frontend Developer",
            bio="Short bio about John.",
            about="About John.",
            github_url="https://github.com/john",
            available_for_work=False,
        )

        self.no_profile_user = User.objects.create_user(
            username="noprof",
            email="noprof@example.com",
            password="StrongPass123!",
        )

        self.published_blog = BlogPost.objects.create(
            profile=self.profile,
            title="Amir Blog",
            content="Published content.",
            status=BlogPost.Status.PUBLISHED,
        )

        self.draft_blog = BlogPost.objects.create(
            profile=self.profile,
            title="Amir Draft",
            content="Draft content.",
            status=BlogPost.Status.DRAFT,
        )

        self.other_published_blog = BlogPost.objects.create(
            profile=self.other_profile,
            title="John Blog",
            content="Other published content.",
            status=BlogPost.Status.PUBLISHED,
        )

        self.parent_comment = Comment.objects.create(
            blog_post=self.published_blog,
            user=self.user,
            content="Parent comment.",
        )

        self.editable_comment = Comment.objects.create(
            blog_post=self.published_blog,
            user=self.user,
            content="Original comment.",
        )

        self.other_blog_comment = Comment.objects.create(
            blog_post=self.other_published_blog,
            user=self.other_user,
            content="Other blog comment.",
        )

    def blog_data(self, **overrides):
        data = {
            "title": "New Blog Post",
            "content": "This is blog content.",
            "status": BlogPost.Status.DRAFT,
        }
        data.update(overrides)
        return data

    def comment_data(self, **overrides):
        data = {
            "content": "Nice post!",
        }
        data.update(overrides)
        return data

    # -------------------------
    # Public blog views
    # -------------------------

    def test_blogpost_view_returns_200(self):
        response = self.client.get(reverse("blog:blogs"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/blogs.html")

    def test_blogpost_view_shows_only_published_posts(self):
        response = self.client.get(reverse("blog:blogs"))

        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        titles = [blog.title for blog in page_obj.object_list]

        self.assertIn("Amir Blog", titles)
        self.assertIn("John Blog", titles)
        self.assertNotIn("Amir Draft", titles)

    def test_blogpost_view_filters_by_query(self):
        response = self.client.get(
            reverse("blog:blogs"),
            {"q": "John"},
        )

        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        titles = [blog.title for blog in page_obj.object_list]

        self.assertIn("John Blog", titles)
        self.assertNotIn("Amir Blog", titles)

    def test_blogpost_details_view_returns_200_for_published_blog(self):
        response = self.client.get(
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/blog_details.html")
        self.assertContains(response, "Amir Blog")

    def test_blogpost_details_view_allows_owner_to_view_draft_blog(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("blog:blog_details", kwargs={"slug": self.draft_blog.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/blog_details.html")
        self.assertContains(response, "Amir Draft")

    def test_blogpost_details_view_hides_draft_blog_from_other_users(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("blog:blog_details", kwargs={"slug": self.draft_blog.slug})
        )

        self.assertEqual(response.status_code, 404)

    # -------------------------
    # Comment views
    # -------------------------

    def test_add_comment_view_requires_login(self):
        response = self.client.get(
            reverse("blog:add_comment", kwargs={"blog_slug": self.published_blog.slug})
        )

        expected = (
            f"{reverse('accounts:login')}?"
            f"next={reverse('blog:add_comment', kwargs={'blog_slug': self.published_blog.slug})}"
        )
        self.assertRedirects(response, expected)

    def test_add_comment_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("blog:add_comment", kwargs={"blog_slug": self.published_blog.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/blog_details.html")

    def test_add_comment_view_post_creates_comment_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:add_comment", kwargs={"blog_slug": self.published_blog.slug}),
            data=self.comment_data(),
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug}),
        )
        self.assertTrue(
            Comment.objects.filter(
                blog_post=self.published_blog,
                user=self.user,
                content="Nice post!",
                parent=None,
            ).exists()
        )
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_add_comment_view_post_creates_reply_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:add_comment", kwargs={"blog_slug": self.published_blog.slug}),
            data=self.comment_data(
                content="This is a reply.",
                parent_id=self.parent_comment.pk,
            ),
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug}),
        )

        reply = Comment.objects.get(
            blog_post=self.published_blog,
            user=self.user,
            content="This is a reply.",
        )
        self.assertEqual(reply.parent, self.parent_comment)
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_add_comment_view_invalid_parent_redirects_back(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:add_comment", kwargs={"blog_slug": self.published_blog.slug}),
            data=self.comment_data(
                content="Invalid reply.",
                parent_id=self.other_blog_comment.pk,
            ),
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug}),
        )
        self.assertFalse(Comment.objects.filter(content="Invalid reply.").exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any("Invalid parent comment." in str(message) for message in messages)
        )

    def test_edit_comment_view_get_redirects(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "blog:edit_comment",
                kwargs={
                    "blog_slug": self.published_blog.slug,
                    "comment_id": self.editable_comment.pk,
                },
            )
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug}),
        )

    def test_edit_comment_view_post_updates_comment_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "blog:edit_comment",
                kwargs={
                    "blog_slug": self.published_blog.slug,
                    "comment_id": self.editable_comment.pk,
                },
            ),
            data=self.comment_data(content="Updated comment."),
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug}),
        )

        self.editable_comment.refresh_from_db()
        self.assertEqual(self.editable_comment.content, "Updated comment.")
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.UPDATED,
            ).exists()
        )

    def test_edit_comment_view_non_owner_returns_404(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                "blog:edit_comment",
                kwargs={
                    "blog_slug": self.published_blog.slug,
                    "comment_id": self.editable_comment.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_comment_view_get_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("blog:delete_comment", kwargs={"pk": self.editable_comment.pk})
        )

        self.assertEqual(response.status_code, 405)

    def test_delete_comment_view_post_deletes_comment_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:delete_comment", kwargs={"pk": self.editable_comment.pk})
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_details", kwargs={"slug": self.published_blog.slug}),
        )
        self.assertFalse(Comment.objects.filter(pk=self.editable_comment.pk).exists())
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.DELETED,
            ).exists()
        )

    # -------------------------
    # My blogs views
    # -------------------------

    def test_my_blogs_view_requires_login(self):
        response = self.client.get(reverse("blog:my_blogs"))

        expected = f"{reverse('accounts:login')}?next={reverse('blog:my_blogs')}"
        self.assertRedirects(response, expected)

    def test_my_blogs_view_without_profile_redirects_create_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(reverse("blog:my_blogs"))

        self.assertRedirects(response, reverse("accounts:create_profile"))

    def test_my_blogs_view_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("blog:my_blogs"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/myblogs.html")

    def test_my_blogs_view_filters_by_status(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("blog:my_blogs"),
            {"status": BlogPost.Status.DRAFT},
        )

        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        titles = [blog.title for blog in page_obj.object_list]

        self.assertIn("Amir Draft", titles)
        self.assertNotIn("Amir Blog", titles)

    # -------------------------
    # Add / edit / delete blog
    # -------------------------

    def test_add_blog_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("blog:add_blog"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/add_blog.html")

    def test_add_blog_view_post_creates_blog_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:add_blog"),
            data={
                **self.blog_data(
                    title="New Blog",
                    status=BlogPost.Status.PUBLISHED,
                ),
                "cover_image": build_image_file(name="cover.jpg"),
            },
        )

        self.assertRedirects(response, reverse("blog:my_blogs"))

        blog = BlogPost.objects.get(title="New Blog")
        self.assertEqual(blog.profile, self.profile)
        self.assertEqual(blog.status, BlogPost.Status.PUBLISHED)
        self.assertIsNotNone(blog.published_at)
        self.assertTrue(blog.cover_image)

        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_add_blog_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:add_blog"),
            data=self.blog_data(title="", content=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/add_blog.html")
        self.assertFalse(BlogPost.objects.filter(title="").exists())
        self.assertIn("title", response.context["blog_form"].errors)

    def test_edit_blog_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("blog:edit_blog", kwargs={"blog_slug": self.published_blog.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/edit_blog.html")

    def test_edit_blog_view_post_updates_blog_and_activity(self):
        self.client.force_login(self.user)

        old_slug = self.published_blog.slug

        response = self.client.post(
            reverse("blog:edit_blog", kwargs={"blog_slug": self.published_blog.slug}),
            data=self.blog_data(
                title="Updated Blog Title",
                content="Updated content.",
                status=BlogPost.Status.PUBLISHED,
            ),
        )

        self.assertRedirects(response, reverse("blog:my_blogs"))

        self.published_blog.refresh_from_db()
        self.assertEqual(self.published_blog.title, "Updated Blog Title")
        self.assertEqual(self.published_blog.content, "Updated content.")
        self.assertEqual(self.published_blog.slug, old_slug)

        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.UPDATED,
            ).exists()
        )

    def test_edit_blog_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:edit_blog", kwargs={"blog_slug": self.published_blog.slug}),
            data=self.blog_data(title="", content=""),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "blog/edit_blog.html")
        self.assertIn("title", response.context["blog_form"].errors)

    def test_delete_blog_view_get_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("blog:delete_blog", kwargs={"pk": self.published_blog.pk})
        )

        self.assertEqual(response.status_code, 405)

    def test_delete_blog_view_post_deletes_blog_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("blog:delete_blog", kwargs={"pk": self.published_blog.pk})
        )

        self.assertRedirects(response, reverse("blog:my_blogs"))
        self.assertFalse(BlogPost.objects.filter(pk=self.published_blog.pk).exists())
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.DELETED,
            ).exists()
        )
