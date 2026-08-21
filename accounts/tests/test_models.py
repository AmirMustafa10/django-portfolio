import os
from io import BytesIO
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from ..models import Profile, User


def build_image_file(
    name="test.jpg", size=(100, 100), image_format="JPEG", noisy=False
):

    if noisy:
        raw = os.urandom(size[0] * size[1] * 3)
        image = Image.frombytes("RGB", size, raw)
    else:
        image = Image.new("RGB", size, "blue")

    buffer = BytesIO()

    save_kwargs = {}
    if image_format.upper() in {"JPEG", "JPG"}:
        save_kwargs["quality"] = 95

    image.save(buffer, format=image_format, **save_kwargs)

    content_type = (
        "image/jpeg"
        if image_format.upper() in {"JPEG", "JPG"}
        else f"image/{image_format.lower()}"
    )

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type=content_type,
    )


def build_pdf_file(name="test.pdf", size_in_mb=1):
    size_in_bytes = size_in_mb * 1024 * 1024
    header = b"%PDF-1.4\n%Fake PDF\n"
    content = header + b"x" * max(0, size_in_bytes - len(header))

    return SimpleUploadedFile(
        name=name,
        content=content,
        content_type="application/pdf",
    )


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="12345678",
        )

    def test_valid_username(self):
        user = User(
            username="valid_user-1",
            email="test1@example.com",
            password="102306589",
        )
        user.full_clean()
        self.assertEqual(user.username, "valid_user-1")

    def test_invalid_username_characters(self):
        user = User(
            username="invalid_usern*&1",
            email="test2@example.com",
            password="102306589",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_username_case_insensitive_duplicate(self):
        user = User(
            username="AMIR",
            email="test3@example.com",
            password="102306589",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_email_case_insensitive_duplicate(self):
        user = User(
            username="amm",
            email="AMIR@example.com",
            password="102306589",
        )
        with self.assertRaises(ValidationError):
            user.full_clean()

    def test_database_case_insensitive_username_constraint(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="Amir",
                email="IntegrityError@mail.com",
                password="102306589",
            )


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="12345678",
        )
        self.user_profile = Profile.objects.create(
            jop_title="Backend",
            user=self.user,
            bio="fewsdoijkwe wd9eokmlk3ewn 9ejwiodsmk ejwqdoms",
            about="asczx edwqksao dwskcol",
            github_url="https://github.com/",
        )

    def test_profile_belongs_to_user(self):
        self.assertEqual(self.user_profile.user, self.user)

    def test_user_cannot_have_multiple_profiles(self):
        profile2 = Profile(
            jop_title="Backend2",
            user=self.user,
            bio="fewsdoijkwe wd9eokmlk3ewn 9ejwiodsmk ejwqdoms",
            about="asczx edwqksao dwskcol",
            github_url="https://github2.com/",
        )

        with self.assertRaises(ValidationError):
            profile2.full_clean()

    def test_valid_avatar(self):
        image = build_image_file(name="avatar.jpg", image_format="JPEG")

        self.user_profile.avatar = image # type: ignore 
        self.user_profile.full_clean()

    def test_avatar_too_large(self):
        image = build_image_file(
            name="large_avatar.png",
            size=(3000, 3000),
            image_format="PNG",
            noisy=True,
        )

        self.user_profile.avatar = image # type: ignore
        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_invalid_avatar_extension(self):
        image = build_image_file(name="avatar.pdf", image_format="JPEG")

        self.user_profile.avatar = image # type: ignore
        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_valid_resume(self):
        resume = build_pdf_file(name="resume.pdf", size_in_mb=1)

        self.user_profile.resume = resume # type: ignore
        self.user_profile.full_clean()

    def test_resume_too_large(self):
        resume = build_pdf_file(name="resume.pdf", size_in_mb=3)

        self.user_profile.resume = resume # type: ignore
        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_invalid_resume_extension(self):
        resume = build_pdf_file(name="resume.jpg", size_in_mb=1)

        self.user_profile.resume = resume # type: ignore
        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_github_url_is_valid(self):
        self.user_profile.github_url = "https://github0.com/"
        self.user_profile.full_clean()

    def test_github_url_is_invalid(self):
        self.user_profile.github_url = "github0"

        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_linkedin_url_is_valid(self):
        self.user_profile.linkedin_url = "https://linkedin.com/"
        self.user_profile.full_clean()

    def test_linkedin_url_is_invalid(self):
        self.user_profile.linkedin_url = "linkedin0"

        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_website_url_is_valid(self):
        self.user_profile.website_url = "https://website.com/"
        self.user_profile.full_clean()

    def test_website_url_is_invalid(self):
        self.user_profile.website_url = "website"

        with self.assertRaises(ValidationError):
            self.user_profile.full_clean()

    def test_available_for_work_with_professional_link_is_valid(self):
        user2 = User.objects.create_user(
            username="ammo",
            email="ammo@yahoo.com",
            password="1456320",
        )

        profile = Profile(
            jop_title="Front",
            user=user2,
            bio="boi",
            about="boiabout",
            github_url="https://github0.com/",
            available_for_work=True,
        )

        profile.full_clean()

    def test_available_for_work_without_professional_link_is_invalid(self):
        user2 = User.objects.create_user(
            username="ammo0",
            email="ammo0@yahoo.com",
            password="1456320",
        )

        profile = Profile(
            jop_title="Front",
            user=user2,
            bio="boi",
            about="boiabout",
            available_for_work=True,
        )

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_get_full_name(self):
        user = User(
            first_name="amm",
            last_name="lamm",
            username="mimi",
            email="mimi@gmail.com",
        )

        profile = Profile(
            jop_title="Front",
            user=user,
            bio="boi",
            about="boiabout",
            available_for_work=True,
        )

        self.assertEqual(profile.get_full_name, "amm lamm")

    def test_str(self):
        self.assertEqual(
            str(self.user_profile),
            "amir's Profile",
        )
