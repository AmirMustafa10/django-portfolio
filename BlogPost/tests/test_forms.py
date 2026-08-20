from io import BytesIO
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from accounts.models import Profile
from ..form import BlogForm, CommentForm
from ..models import BlogPost

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


class BlogFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )

        self.profile = Profile.objects.create(
            user=self.user,
            jop_title="Backend Developer",
            bio="Short bio about Amir.",
            about="About Amir.",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

    def valid_data(self, **overrides):
        data = {
            "title": "My First Blog Post",
            "content": "This is the blog content.",
            "status": BlogPost.Status.DRAFT,
        }
        data.update(overrides)
        return data

    def test_valid_blog_form_draft(self):
        form = BlogForm(data=self.valid_data())

        self.assertTrue(form.is_valid())

    def test_valid_blog_form_published(self):
        form = BlogForm(
            data=self.valid_data(
                status=BlogPost.Status.PUBLISHED,
            )
        )

        self.assertTrue(form.is_valid())

    def test_blog_form_missing_title(self):
        form = BlogForm(data=self.valid_data(title=""))

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_blog_form_missing_content(self):
        form = BlogForm(data=self.valid_data(content=""))

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_blog_form_invalid_cover_image_extension(self):
        invalid_image = SimpleUploadedFile(
            name="cover.txt",
            content=b"not an image",
            content_type="text/plain",
        )

        form = BlogForm(
            data=self.valid_data(),
            files={"cover_image": invalid_image},
        )

        self.assertFalse(form.is_valid())
        self.assertIn("cover_image", form.errors)

    def test_blog_form_valid_cover_image(self):
        form = BlogForm(
            data=self.valid_data(),
            files={"cover_image": build_image_file(name="cover.jpg")},
        )

        self.assertTrue(form.is_valid())

    def test_blog_form_save_generates_slug_and_sets_profile(self):
        form = BlogForm(
            data=self.valid_data(
                title="DevConnect Blog",
                status=BlogPost.Status.PUBLISHED,
            )
        )

        self.assertTrue(form.is_valid())

        post = form.save(commit=False)
        post.profile = self.profile
        post.save()

        self.assertEqual(post.slug, "devconnect-blog")
        self.assertEqual(post.profile, self.profile)
        self.assertEqual(post.status, BlogPost.Status.PUBLISHED)
        self.assertIsNotNone(post.published_at)

    def test_blog_form_save_draft_has_no_published_at(self):
        form = BlogForm(
            data=self.valid_data(
                title="Draft Post",
                status=BlogPost.Status.DRAFT,
            )
        )

        self.assertTrue(form.is_valid())

        post = form.save(commit=False)
        post.profile = self.profile
        post.save()

        self.assertIsNone(post.published_at)


class CommentFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )

        self.profile = Profile.objects.create(
            user=self.user,
            jop_title="Backend Developer",
            bio="Short bio about Amir.",
            about="About Amir.",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

        self.post = BlogPost.objects.create(
            profile=self.profile,
            title="My Blog Post",
            content="Post content.",
        )

    def test_valid_comment_form(self):
        form = CommentForm(
            data={
                "content": "Nice post!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_comment_form_missing_content(self):
        form = CommentForm(
            data={
                "content": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_comment_form_trimmed_content_on_save(self):
        form = CommentForm(
            data={
                "content": "   Great post!   ",
            }
        )

        self.assertTrue(form.is_valid())

        comment = form.save(commit=False)
        comment.blog_post = self.post
        comment.user = self.user
        comment.save()

        self.assertEqual(comment.content, "Great post!")

    # if deleted user
    def test_comment_form_can_save_anonymous_comment(self):
        form = CommentForm(
            data={
                "content": "Anonymous comment.",
            }
        )

        self.assertTrue(form.is_valid())

        comment = form.save(commit=False)
        comment.blog_post = self.post
        comment.save()

        self.assertIsNone(comment.user)
        self.assertEqual(comment.content, "Anonymous comment.")
