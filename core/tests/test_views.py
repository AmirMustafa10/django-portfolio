from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from accounts.models import Profile
from ..models import Activity
from portfolio.models import Project, Skill
from BlogPost.models import BlogPost

User = get_user_model()


class CoreViewsTest(TestCase):

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
            username="john2",
            email="john2@example.com",
            password="StrongPass123!",
            first_name="John2",
            last_name="Doe2",
        )

        self.skill = Skill.objects.create(name="Python")
        self.profile.skills.add(self.skill)

        self.project = Project.objects.create(
            profile=self.profile,
            title="DevConnect",
            description="Portfolio platform.",
        )
        self.project.skills.add(self.skill)

        self.published_blog = BlogPost.objects.create(
            profile=self.profile,
            title="My Published Blog",
            content="Blog content.",
            status=BlogPost.Status.PUBLISHED,
        )

        self.draft_blog = BlogPost.objects.create(
            profile=self.profile,
            title="My Draft Blog",
            content="Draft content.",
            status=BlogPost.Status.DRAFT,
        )

        self.activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.project,
        )

    def test_home_view_returns_200(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_home_view_contains_developers(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "amir")
        self.assertContains(response, "john")

    def test_dashboard_view_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        expected = f"{reverse('accounts:login')}?next={reverse('dashboard')}"
        self.assertRedirects(response, expected)

    def test_dashboard_view_without_profile_redirects_create_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, reverse("accounts:create_profile"))

        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Create your profile first before view your dashboard." in str(m)
                for m in messages_list
            )
        )

    def test_dashboard_view_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/dashboard.html")

    def test_dashboard_view_context_contains_profile_and_stats(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"], self.profile)

        stats = response.context["stats"]
        self.assertEqual(stats["projects_count"], 1)
        self.assertEqual(stats["published_blogs_count"], 1)
        self.assertEqual(stats["draft_blogs_count"], 1)
        self.assertEqual(stats["skills_count"], 1)

    def test_dashboard_view_contains_recent_objects(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)

        recent_projects = response.context["recent_projects"]
        recent_blogs = response.context["recent_blogs"]
        recent_activities = response.context["recent_activities"]

        self.assertEqual(list(recent_projects)[0], self.project)
        self.assertEqual(list(recent_blogs)[0], self.draft_blog)
        self.assertEqual(list(recent_activities)[0], self.activity)

    def test_activity_view_requires_login(self):
        response = self.client.get(reverse("activity"))

        expected = f"{reverse('accounts:login')}?next={reverse('activity')}"
        self.assertRedirects(response, expected)

    def test_activity_view_without_profile_redirects_create_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(reverse("activity"))

        self.assertRedirects(response, reverse("accounts:create_profile"))

        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(
            any(
                "Create your profile first before view your activity." in str(m)
                for m in messages_list
            )
        )

    def test_activity_view_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("activity"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/activity.html")

    def test_activity_view_paginates_results(self):
        self.client.force_login(self.user)

        for index in range(12):
            Activity.objects.create(
                user=self.user,
                action=Activity.Action.UPDATED,
                target=self.project,
            )

        response = self.client.get(reverse("activity"))

        self.assertEqual(response.status_code, 200)
        page_obj = response.context["page_obj"]

        self.assertEqual(page_obj.number, 1)
        self.assertTrue(page_obj.has_next())
        self.assertLessEqual(len(page_obj.object_list), 10)
