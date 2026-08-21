from datetime import timedelta
from io import BytesIO
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from accounts.models import Profile, User
from ..models import BlogPost, Comment


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


class BlogPostModelTest(TestCase):

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

    def test_blog_post_slug_is_generated_automatically(self):
        post = BlogPost.objects.create(
            profile=self.profile,
            title="My First Blog Post",
            content="This is the blog content.",
        )

        self.assertEqual(post.slug, "my-first-blog-post")

    def test_blog_post_slug_handles_duplicate_slug(self):
        first_post = BlogPost.objects.create(
            profile=self.profile,
            title="My Blog Post",
            content="First post content.",
        )

        second_post = BlogPost.objects.create(
            profile=self.profile,
            title="My Blog Post",
            content="Second post content.",
        )

        self.assertEqual(first_post.slug, "my-blog-post")
        self.assertEqual(second_post.slug, "my-blog-post-1")

    def test_published_post_sets_published_at_automatically(self):
        post = BlogPost.objects.create(
            profile=self.profile,
            title="Published Post",
            content="Published content.",
            status=BlogPost.Status.PUBLISHED,
        )

        self.assertIsNotNone(post.published_at)
        self.assertEqual(post.status, BlogPost.Status.PUBLISHED)

    def test_draft_post_has_no_published_at(self):
        post = BlogPost.objects.create(
            profile=self.profile,
            title="Draft Post",
            content="Draft content.",
            status=BlogPost.Status.DRAFT,
        )

        self.assertIsNone(post.published_at)
        self.assertEqual(post.status, BlogPost.Status.DRAFT)

    def test_published_post_with_manual_published_at_is_valid(self):
        post = BlogPost(
            profile=self.profile,
            title="Manually Published",
            content="Published content.",
            status=BlogPost.Status.PUBLISHED,
            published_at=timezone.now() - timedelta(days=1),
            slug="manually-published",
        )

        post.full_clean()

    def test_published_post_without_slug_gets_slug_before_clean(self):
        post = BlogPost(
            profile=self.profile,
            title="Slug Before Clean",
            content="Content.",
            status=BlogPost.Status.PUBLISHED,
            published_at=timezone.now(),
        )

        post.save()

        self.assertEqual(post.slug, "slug-before-clean")

    def test_blog_post_str_returns_title(self):
        post = BlogPost.objects.create(
            profile=self.profile,
            title="DevConnect Blog",
            content="Blog content.",
        )

        self.assertEqual(str(post), "DevConnect Blog")

    def test_cover_image_is_optional(self):
        post = BlogPost.objects.create(
            profile=self.profile,
            title="No Cover Image",
            content="Content.",
        )

        self.assertIsNone(post.cover_image.name if post.cover_image else None)

    def test_blog_post_cover_image_valid(self):
        post = BlogPost(
            profile=self.profile,
            title="Image Post",
            content="Content.",
            slug="image-post",
            cover_image=build_image_file(name="cover.jpg"),
        )

        post.full_clean()

    def test_blog_post_cover_image_invalid_extension(self):
        invalid_image = SimpleUploadedFile(
            name="cover.txt",
            content=b"not an image",
            content_type="text/plain",
        )

        post = BlogPost(
            profile=self.profile,
            title="Invalid Image Post",
            content="Content.",
            slug="invalid-image-post",
            cover_image=invalid_image,
        )

        with self.assertRaises(ValidationError):
            post.full_clean()


class CommentModelTest(TestCase):

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

        self.post = BlogPost.objects.create(
            profile=self.profile,
            title="My Blog Post",
            content="Post content.",
        )

        self.comment = Comment.objects.create(
            blog_post=self.post,
            user=self.user,
            content="Nice post!",
        )

    def test_comment_str_returns_user_and_blog_title(self):
        self.assertEqual(
            str(self.comment),
            "comment amir - My Blog Post",
        )

    def test_comment_content_is_trimmed(self):
        comment = Comment(
            blog_post=self.post,
            user=self.user,
            content="   Great post!   ",
        )

        comment.save()

        self.assertEqual(comment.content, "Great post!")

    def test_empty_comment_is_invalid(self):
        comment = Comment(
            blog_post=self.post,
            user=self.user,
            content="   ",
        )

        with self.assertRaises(ValidationError):
            comment.full_clean()

    def test_reply_must_belong_to_same_blog_post(self):
        other_post = BlogPost.objects.create(
            profile=self.profile,
            title="Other Blog Post",
            content="Other content.",
        )

        parent_comment = Comment.objects.create(
            blog_post=self.post,
            user=self.user,
            content="Parent comment.",
        )

        reply = Comment(
            blog_post=other_post,
            user=self.user,
            parent=parent_comment,
            content="Reply content.",
        )

        with self.assertRaises(ValidationError):
            reply.full_clean()

    def test_reply_on_same_blog_post_is_valid(self):
        parent_comment = Comment.objects.create(
            blog_post=self.post,
            user=self.user,
            content="Parent comment.",
        )

        reply = Comment(
            blog_post=self.post,
            user=self.user,
            parent=parent_comment,
            content="Reply content.",
        )

        reply.full_clean()

    # if user deleted
    def test_comment_without_user_is_valid(self):
        comment = Comment(
            blog_post=self.post,
            content="Anonymous comment.",
        )

        comment.full_clean()
