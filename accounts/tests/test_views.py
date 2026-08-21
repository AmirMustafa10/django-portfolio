from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from core.models import Activity
from portfolio.models import Skill
from accounts.models import Profile

User = get_user_model()


class AccountsViewsTest(TestCase):

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
            first_name="No",
            last_name="Profile",
        )

    def valid_profile_data(self, **overrides):
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

    def valid_user_data(self, **overrides):
        data = {
            "first_name": "Amir",
            "last_name": "Mustafa",
            "email": "amir.updated@example.com",
            "username": "amir_updated",
        }
        data.update(overrides)
        return data

    # -------------------------
    # register / login / logout
    # -------------------------

    def test_register_view_get_anonymous_returns_200(self):
        response = self.client.get(reverse("accounts:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_view_authenticated_redirects_home(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:register"))

        self.assertRedirects(response, reverse("home"))

    def test_register_view_post_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            User.objects.get(username="newuser").pk,
        )

    def test_login_view_get_anonymous_returns_200(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_view_authenticated_redirects_home(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:login"))

        self.assertRedirects(response, reverse("home"))

    def test_login_view_post_with_username_logs_in(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "amir",
                "password": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )

    def test_login_view_post_with_email_logs_in(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "amir@example.com",
                "password": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk,
        )

    def test_login_view_invalid_credentials_renders_form(self):
        response = self.client.post(
            reverse("accounts:login"),
            data={
                "username": "amir",
                "password": "WrongPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")
        self.assertContains(response, "Invalid username/email or password.")

    def test_logout_view_redirects_home_and_logs_out(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    # -------------------------
    # developers list
    # -------------------------

    def test_developers_view_returns_200(self):
        response = self.client.get(reverse("accounts:developers"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/developers.html")

    def test_developers_view_filters_by_query(self):
        response = self.client.get(
            reverse("accounts:developers"),
            {"q": "john"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "john")
        self.assertNotContains(response, "hala")

    def test_developers_view_filters_by_availability(self):
        response = self.client.get(
            reverse("accounts:developers"),
            {"availability": "available"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "amir")
        self.assertNotContains(response, "john")

    # -------------------------
    # developer detail
    # -------------------------

    def test_developer_detail_view_returns_200(self):
        response = self.client.get(
            reverse(
                "accounts:developer_detail",
                kwargs={"username": self.user.username},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/developer_detail.html")
        self.assertContains(response, "@amir")

    def test_developer_detail_view_nonexistent_user_returns_404(self):
        response = self.client.get(
            reverse(
                "accounts:developer_detail",
                kwargs={"username": "doesnotexist"},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_developer_detail_view_self_without_profile_redirects_create_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(
            reverse(
                "accounts:developer_detail",
                kwargs={"username": self.no_profile_user.username},
            )
        )

        self.assertRedirects(response, reverse("accounts:create_profile"))

    # -------------------------
    # create profile
    # -------------------------

    def test_create_profile_view_requires_login(self):
        response = self.client.get(reverse("accounts:create_profile"))

        expected = (
            f"{reverse('accounts:login')}?next={reverse('accounts:create_profile')}"
        )
        self.assertRedirects(response, expected)

    def test_create_profile_view_get_returns_200(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(reverse("accounts:create_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/create_profile.html")

    def test_create_profile_view_user_with_profile_redirects_detail(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:create_profile"))

        self.assertRedirects(
            response,
            reverse(
                "accounts:developer_detail",
                kwargs={"username": self.user.username},
            ),
        )

    def test_create_profile_view_post_creates_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.post(
            reverse("accounts:create_profile"),
            data={
                "first_name": "No",
                "last_name": "Profile",
                "email": "noprof.updated@example.com",
                "username": "noprof",
                "jop_title": "Backend Developer",
                "bio": "Short bio about the developer.",
                "about": "More details about the developer.",
                "github_url": "https://github.com/noprof",
                "linkedin_url": "",
                "website_url": "",
                "location": "Cairo",
                "available_for_work": True,
                "skills": [],
                "new_skills": [],
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "accounts:developer_detail",
                kwargs={"username": self.no_profile_user.username},
            ),
        )
        self.assertTrue(Profile.objects.filter(user=self.no_profile_user).exists())

    # -------------------------
    # edit profile
    # -------------------------

    def test_edit_profile_view_requires_login(self):
        response = self.client.get(reverse("accounts:edit_profile"))

        expected = (
            f"{reverse('accounts:login')}?next={reverse('accounts:edit_profile')}"
        )
        self.assertRedirects(response, expected)

    def test_edit_profile_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:edit_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")

    def test_edit_profile_view_post_updates_profile_and_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_profile"),
            data={
                "first_name": "Amir Updated",
                "last_name": "Mustafa Updated",
                "email": "amir.updated@example.com",
                "username": "amir_updated",
                "jop_title": "Senior Backend Developer",
                "bio": "Updated bio.",
                "about": "Updated about section.",
                "github_url": "https://github.com/amir_updated",
                "linkedin_url": "",
                "website_url": "",
                "location": "Alexandria",
                "available_for_work": True,
                "skills": [],
                "new_skills": [],
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "accounts:developer_detail",
                kwargs={"username": "amir_updated"},
            ),
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.username, "amir_updated")
        self.assertEqual(self.user.email, "amir.updated@example.com")
        self.assertEqual(self.profile.jop_title, "Senior Backend Developer")
        self.assertEqual(self.profile.location, "Alexandria")

    def test_create_profile_view_post_creates_profile_skills_and_activity(self):
        self.client.force_login(self.no_profile_user)

        python_skill = Skill.objects.create(name="Python")

        response = self.client.post(
            reverse("accounts:create_profile"),
            data={
                "first_name": "No",
                "last_name": "Profile",
                "email": "noprof.updated@example.com",
                "username": "noprof",
                "jop_title": "Backend Developer",
                "bio": "Short bio about the developer.",
                "about": "More details about the developer.",
                "github_url": "https://github.com/noprof",
                "linkedin_url": "",
                "website_url": "",
                "location": "Cairo",
                "available_for_work": True,
                "skills": [str(python_skill.pk)],
                "new_skills": ["Django"],
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "accounts:developer_detail",
                kwargs={"username": self.no_profile_user.username},
            ),
        )

        profile = Profile.objects.get(user=self.no_profile_user)

        self.assertSetEqual(
            set(profile.skills.values_list("name", flat=True)),
            {"Python", "Django"},
        )

        self.assertTrue(
            Skill.objects.filter(name="Django").exists()
        )

        self.assertTrue(
            Activity.objects.filter(
                user=self.no_profile_user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_edit_profile_view_post_updates_user_profile_skills_and_activity(self):
        self.client.force_login(self.user)

        python_skill = Skill.objects.create(name="Python")
        Skill.objects.create(name="Django")

        response = self.client.post(
            reverse("accounts:edit_profile"),
            data={
                "first_name": "Amir Updated",
                "last_name": "Mustafa Updated",
                "email": "amir.updated@example.com",
                "username": "amir_updated",
                "jop_title": "Senior Backend Developer",
                "bio": "Updated bio.",
                "about": "Updated about section.",
                "github_url": "https://github.com/amir_updated",
                "linkedin_url": "",
                "website_url": "",
                "location": "Alexandria",
                "available_for_work": True,
                "skills": [str(python_skill.pk)],
                "new_skills": ["Django"],
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "accounts:developer_detail",
                kwargs={"username": "amir_updated"},
            ),
        )

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.username, "amir_updated")
        self.assertEqual(self.user.email, "amir.updated@example.com")
        self.assertEqual(self.profile.jop_title, "Senior Backend Developer")
        self.assertEqual(self.profile.location, "Alexandria")

        self.assertSetEqual(
            set(self.profile.skills.values_list("name", flat=True)),
            {"Python", "Django"},
        )

        activity = Activity.objects.filter(
            user=self.user,
            action=Activity.Action.UPDATED,
        ).first()

        self.assertIsNotNone(activity)
        self.assertEqual(activity.target, self.profile)
        
    def test_create_profile_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.post(
            reverse("accounts:create_profile"),
            data={
                "first_name": "No",
                "last_name": "Profile",
                "email": "noprof.updated@example.com",
                "username": "noprof",
                "jop_title": "Backend Developer",
                "bio": "Short bio about the developer.",
                "about": "More details about the developer.",
                "github_url": "",
                "linkedin_url": "",
                "website_url": "",
                "location": "Cairo",
                "available_for_work": True,
                "skills": [],
                "new_skills": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/create_profile.html")
        self.assertFalse(Profile.objects.filter(user=self.no_profile_user).exists())
        self.assertContains(response, "At least one professional link")


    def test_edit_profile_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:edit_profile"),
            data={
                "first_name": "Amir Updated",
                "last_name": "Mustafa Updated",
                "email": "amir.updated@example.com",
                "username": "amir_updated",
                "jop_title": "Senior Backend Developer",
                "bio": "Updated bio.",
                "about": "Updated about section.",
                "github_url": "",
                "linkedin_url": "",
                "website_url": "",
                "location": "Alexandria",
                "available_for_work": True,
                "skills": [],
                "new_skills": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")
        self.assertContains(response, "At least one professional link")

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.username, "amir")
        self.assertEqual(self.profile.jop_title, "Backend Developer")
        
    def test_developers_view_paginates_results(self):
        for index in range(10):
            user = User.objects.create_user(
                username=f"user{index}",
                email=f"user{index}@example.com",
                password="StrongPass123!",
            )
    
            Profile.objects.create(
                user=user,
                jop_title="Developer",
                bio="Bio",
                about="About",
                github_url=f"https://github.com/user{index}",
                available_for_work=True,
            )
    
        response = self.client.get(
            reverse("accounts:developers"),
            {"page": 2},
        )
    
        self.assertEqual(response.status_code, 200)
    
        page_obj = response.context["page_obj"]
    
        self.assertEqual(page_obj.number, 2)
        self.assertTrue(page_obj.has_previous())