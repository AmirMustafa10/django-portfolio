from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from ..forms import LoginForm, ProfileForm, RegisterForm, UserForm
from ..models import Profile

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


def build_pdf_file(name="test.pdf"):
    content = b"%PDF-1.4\n%Fake PDF\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

    return SimpleUploadedFile(
        name=name,
        content=content,
        content_type="application/pdf",
    )


class RegisterFormTest(TestCase):

    def setUp(self):
        self.existing_user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            first_name="Amir",
            last_name="Mustafa",
            password="StrongPass123!",
        )

    def test_valid_register_form(self):
        form = RegisterForm(
            data={
                "username": "john",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

    def test_register_form_password_mismatch(self):
        form = RegisterForm(
            data={
                "username": "john",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "StrongPass123!",
                "confirm_password": "DifferentPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_register_form_duplicate_username(self):
        form = RegisterForm(
            data={
                "username": "AMIR",
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_register_form_duplicate_email(self):
        form = RegisterForm(
            data={
                "username": "newuser",
                "email": "AMIR@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_register_form_save_hashes_password(self):
        form = RegisterForm(
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            }
        )

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertNotEqual(user.password, "StrongPass123!")


class LoginFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.request = RequestFactory().post("/accounts/login/")

    def test_login_form_with_username_is_valid(self):
        form = LoginForm(
            request=self.request,
            data={
                "username": "amir",
                "password": "StrongPass123!",
            },
        )

        self.assertTrue(form.is_valid())

    def test_login_form_with_email_is_valid(self):
        form = LoginForm(
            request=self.request,
            data={
                "username": "amir@example.com",
                "password": "StrongPass123!",
            },
        )

        self.assertTrue(form.is_valid())

    def test_login_form_invalid_credentials(self):
        form = LoginForm(
            request=self.request,
            data={
                "username": "amir",
                "password": "WrongPass123!",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)


class UserFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            first_name="Amir",
            last_name="Mustafa",
            password="StrongPass123!",
        )

        self.other_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            first_name="John",
            last_name="Doe",
            password="StrongPass123!",
        )

    def test_valid_user_form(self):
        form = UserForm(
            data={
                "first_name": "Amir Updated",
                "last_name": "Mustafa Updated",
                "email": "amir.updated@example.com",
                "username": "amir_updated",
            },
            instance=self.user,
        )

        self.assertTrue(form.is_valid())

        updated_user = form.save()
        self.assertEqual(updated_user.username, "amir_updated")
        self.assertEqual(updated_user.email, "amir.updated@example.com")

    def test_user_form_duplicate_username(self):
        form = UserForm(
            data={
                "first_name": "Amir",
                "last_name": "Mustafa",
                "email": "amir.new@example.com",
                "username": "JOHN",
            },
            instance=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_user_form_duplicate_email(self):
        form = UserForm(
            data={
                "first_name": "Amir",
                "last_name": "Mustafa",
                "email": "JOHN@EXAMPLE.COM",
                "username": "amir_updated",
            },
            instance=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class ProfileFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.profile = Profile(user=self.user)

    def profile_data(self, **overrides):
        data = {
            "jop_title": "Backend Developer",
            "bio": "Short bio about the developer.",
            "about": "More details about the developer.",
            "github_url": "https://github.com/amir",
            "linkedin_url": "",
            "website_url": "",
            "location": "Cairo",
            "available_for_work": True,
        }
        data.update(overrides)
        return data

    def test_valid_profile_form(self):
        form = ProfileForm(
            data=self.profile_data(),
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_profile_form_requires_professional_link_when_available_for_work(self):
        form = ProfileForm(
            data=self.profile_data(
                github_url="",
                linkedin_url="",
                website_url="",
                available_for_work=True,
            ),
            instance=self.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_profile_form_valid_without_available_for_work(self):
        form = ProfileForm(
            data=self.profile_data(
                github_url="",
                linkedin_url="",
                website_url="",
                available_for_work=False,
            ),
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_valid_avatar(self):
        form = ProfileForm(
            data=self.profile_data(),
            files={"avatar": build_image_file(name="avatar.jpg", image_format="JPEG")}, # pyright: ignore[reportArgumentType]
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_invalid_avatar_extension(self):
        invalid_avatar = SimpleUploadedFile(
            name="avatar.txt",
            content=b"not an image",
            content_type="text/plain",
        )

        form = ProfileForm(
            data=self.profile_data(),
            files={"avatar": invalid_avatar}, # type: ignore
            instance=self.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("avatar", form.errors)

    def test_valid_resume(self):
        form = ProfileForm(
            data=self.profile_data(),
            files={"resume": build_pdf_file(name="resume.pdf")}, # pyright: ignore[reportArgumentType]
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_invalid_resume_extension(self):
        invalid_resume = SimpleUploadedFile(
            name="resume.jpg",
            content=b"not a pdf",
            content_type="image/jpeg",
        )

        form = ProfileForm(
            data=self.profile_data(),
            files={"resume": invalid_resume}, # pyright: ignore[reportArgumentType]
            instance=self.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("resume", form.errors)

    def test_github_url_is_valid(self):
        form = ProfileForm(
            data=self.profile_data(github_url="https://github.com/amir"),
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_github_url_is_invalid(self):
        form = ProfileForm(
            data=self.profile_data(github_url="github"),
            instance=self.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_linkedin_url_is_valid(self):
        form = ProfileForm(
            data=self.profile_data(linkedin_url="https://linkedin.com/in/amir"),
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_linkedin_url_is_invalid(self):
        form = ProfileForm(
            data=self.profile_data(linkedin_url="linkedin0"),
            instance=self.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("linkedin_url", form.errors)

    def test_website_url_is_valid(self):
        form = ProfileForm(
            data=self.profile_data(website_url="https://website.com"),
            instance=self.profile,
        )

        self.assertTrue(form.is_valid())

    def test_website_url_is_invalid(self):
        form = ProfileForm(
            data=self.profile_data(website_url="website"),
            instance=self.profile,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("website_url", form.errors)

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
        profile = Profile(
            jop_title="Backend",
            user=self.user,
            bio="bio",
            about="about",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

        self.assertEqual(str(profile), "amir's Profile")
