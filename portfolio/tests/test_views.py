from datetime import date
from io import BytesIO
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from accounts.models import Profile
from core.models import Activity
from portfolio.models import Education, Experience, Project, ProjectImage, Skill

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


class PortfolioViewsTest(TestCase):

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

        self.python_skill = Skill.objects.create(name="Python")
        self.django_skill = Skill.objects.create(name="Django")
        self.react_skill = Skill.objects.create(name="React")

        self.experience = Experience.objects.create(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            description="Worked on backend systems.",
            start_date=date(2024, 1, 1),
            end_date=date(2025, 1, 1),
            currently_working=False,
        )

        self.education = Education.objects.create(
            profile=self.profile,
            institution="Cairo University",
            degree="BSc",
            field_of_study="Computer Science",
            start_date=date(2020, 1, 1),
            end_date=date(2024, 1, 1),
            grade="Very Good",
            description="Studied software engineering.",
        )

        self.project = Project.objects.create(
            profile=self.profile,
            title="DevConnect",
            description="Portfolio platform.",
            status=Project.Status.IN_PROGRESS,
        )
        self.project.skills.add(self.python_skill)

        self.completed_project = Project.objects.create(
            profile=self.other_profile,
            title="Completed App",
            description="A completed app.",
            status=Project.Status.COMPLETED,
            live_demo_url="https://example.com",
        )
        self.completed_project.skills.add(self.django_skill)

        self.project_image = ProjectImage.objects.create(
            project=self.project,
            image=build_image_file(name="project.jpg"),
            caption="Cover",
            display_order=1,
        )

    def experience_data(self, **overrides):
        data = {
            "company_name": "Meta",
            "job_title": "Backend Engineer",
            "employment_type": Experience.EmploymentType.FULL_TIME,
            "description": "Built backend services.",
            "start_date": date(2023, 1, 1),
            "end_date": date(2024, 1, 1),
            "currently_working": False,
        }
        data.update(overrides)
        return data

    def education_data(self, **overrides):
        data = {
            "institution": "AUC",
            "degree": "Bachelor",
            "field_of_study": "Computer Science",
            "start_date": date(2019, 1, 1),
            "end_date": date(2023, 1, 1),
            "grade": "Excellent",
            "description": "Studied CS.",
        }
        data.update(overrides)
        return data

    def project_data(self, **overrides):
        data = {
            "title": "My New Project",
            "description": "A brand new project.",
            "status": Project.Status.IN_PROGRESS,
            "live_demo_url": "",
            "source_code_url": "",
            "is_featured": False,
        }
        data.update(overrides)
        return data

    # -------------------------
    # Public project views
    # -------------------------

    def test_projects_view_returns_200(self):
        response = self.client.get(reverse("portfolio:projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/Projects.html")

    def test_projects_view_filters_by_query(self):
        response = self.client.get(
            reverse("portfolio:projects"),
            {"q": "DevConnect"},
        )

        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        titles = [project.title for project in page_obj.object_list]

        self.assertIn("DevConnect", titles)
        self.assertNotIn("Completed App", titles)

    def test_projects_view_filters_by_status(self):
        response = self.client.get(
            reverse("portfolio:projects"),
            {"status": Project.Status.COMPLETED},
        )

        self.assertEqual(response.status_code, 200)

        page_obj = response.context["page_obj"]
        titles = [project.title for project in page_obj.object_list]

        self.assertIn("Completed App", titles)
        self.assertNotIn("DevConnect", titles)

    def test_project_details_view_returns_200(self):
        response = self.client.get(
            reverse("portfolio:project_details", kwargs={"slug": self.project.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/project_details.html")
        self.assertContains(response, "DevConnect")

    def test_project_details_view_nonexistent_returns_404(self):
        response = self.client.get(
            reverse("portfolio:project_details", kwargs={"slug": "does-not-exist"})
        )

        self.assertEqual(response.status_code, 404)

    # -------------------------
    # Experience views
    # -------------------------

    def test_add_experience_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("portfolio:add_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/experience/add_experience.html")

    def test_add_experience_view_post_creates_experience_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:add_experience"),
            data=self.experience_data(),
        )

        self.assertRedirects(response, reverse("accounts:edit_profile"))
        self.assertTrue(
            Experience.objects.filter(
                profile=self.profile,
                company_name="Meta",
                job_title="Backend Engineer",
            ).exists()
        )
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_add_experience_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:add_experience"),
            data=self.experience_data(
                currently_working=True,
                end_date=date(2024, 1, 1),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/experience/add_experience.html")
        self.assertFalse(
            Experience.objects.filter(
                profile=self.profile,
                company_name="Meta",
            ).exists()
        )
        self.assertIn("end_date", response.context["experience_form"].errors)

    def test_edit_experience_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("portfolio:edit_experience", kwargs={"pk": self.experience.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/experience/edit_experience.html")

    def test_edit_experience_view_post_updates_experience_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:edit_experience", kwargs={"pk": self.experience.pk}),
            data=self.experience_data(
                company_name="Meta Updated",
                job_title="Senior Backend Engineer",
            ),
        )

        self.assertRedirects(response, reverse("accounts:edit_profile"))

        self.experience.refresh_from_db()

        self.assertEqual(self.experience.company_name, "Meta Updated")
        self.assertEqual(self.experience.job_title, "Senior Backend Engineer")
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.UPDATED,
            ).exists()
        )

    def test_delete_experience_view_post_deletes_experience_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:delete_experience", kwargs={"pk": self.experience.pk})
        )

        self.assertRedirects(response, reverse("accounts:edit_profile"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.DELETED,
            ).exists()
        )

    # -------------------------
    # Education views
    # -------------------------

    def test_add_education_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("portfolio:add_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/education/add_education.html")

    def test_add_education_view_post_creates_education_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:add_education"),
            data=self.education_data(
                institution="AUC",
                degree="Bachelor",
            ),
        )

        self.assertRedirects(response, reverse("accounts:edit_profile"))
        self.assertTrue(
            Education.objects.filter(
                profile=self.profile,
                institution="AUC",
                degree="Bachelor",
            ).exists()
        )
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_add_education_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:add_education"),
            data=self.education_data(
                start_date=date(2024, 1, 1),
                end_date=date(2023, 1, 1),
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/education/add_education.html")
        self.assertFalse(
            Education.objects.filter(
                profile=self.profile,
                institution="AUC",
            ).exists()
        )
        self.assertIn("end_date", response.context["education_form"].errors)

    def test_edit_education_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("portfolio:edit_education", kwargs={"pk": self.education.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/education/edit_education.html")

    def test_edit_education_view_post_updates_education_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:edit_education", kwargs={"pk": self.education.pk}),
            data=self.education_data(
                institution="AUC Updated",
                degree="Master",
            ),
        )

        self.assertRedirects(response, reverse("accounts:edit_profile"))

        self.education.refresh_from_db()

        self.assertEqual(self.education.institution, "AUC Updated")
        self.assertEqual(self.education.degree, "Master")
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.UPDATED,
            ).exists()
        )

    def test_delete_education_view_post_deletes_education_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:delete_education", kwargs={"pk": self.education.pk})
        )

        self.assertRedirects(response, reverse("accounts:edit_profile"))
        self.assertFalse(Education.objects.filter(pk=self.education.pk).exists())
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.DELETED,
            ).exists()
        )

    # -------------------------
    # Project views
    # -------------------------

    def test_my_projects_view_requires_login(self):
        response = self.client.get(reverse("portfolio:my_projects"))

        expected = (
            f"{reverse('accounts:login')}?next={reverse('portfolio:my_projects')}"
        )
        self.assertRedirects(response, expected)

    def test_my_projects_view_without_profile_redirects_create_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(reverse("portfolio:my_projects"))

        self.assertRedirects(response, reverse("accounts:create_profile"))

    def test_my_projects_view_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("portfolio:my_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/my_projects.html")

    def test_add_project_view_requires_login(self):
        response = self.client.get(reverse("portfolio:add_project"))

        expected = (
            f"{reverse('accounts:login')}?next={reverse('portfolio:add_project')}"
        )
        self.assertRedirects(response, expected)

    def test_add_project_view_without_profile_redirects_create_profile(self):
        self.client.force_login(self.no_profile_user)

        response = self.client.get(reverse("portfolio:add_project"))

        self.assertRedirects(response, reverse("accounts:create_profile"))

    def test_add_project_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("portfolio:add_project"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/add_project.html")

    def test_add_project_view_post_creates_project_skills_images_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:add_project"),
            data={
                **self.project_data(
                    title="New Portfolio App",
                    description="A brand new portfolio app.",
                    status=Project.Status.IN_PROGRESS,
                ),
                "skills": [str(self.python_skill.pk)],
                "new_skills": ["Django"],
                "project_images": [build_image_file(name="cover.jpg")],
            },
        )

        self.assertRedirects(response, reverse("portfolio:my_projects"))

        project = Project.objects.get(title="New Portfolio App")
        self.assertEqual(project.profile, self.profile)

        self.assertSetEqual(
            set(project.skills.values_list("name", flat=True)),
            {"Python"},
        )

        self.assertEqual(project.images.count(), 1)
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.CREATED,
            ).exists()
        )

    def test_add_project_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:add_project"),
            data=self.project_data(
                title="Invalid Completed Project",
                status=Project.Status.COMPLETED,
                live_demo_url="",
                source_code_url="",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/add_project.html")
        self.assertFalse(
            Project.objects.filter(title="Invalid Completed Project").exists()
        )
        self.assertIn("status", response.context["project_form"].errors)

    def test_edit_project_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("portfolio:edit_project", kwargs={"slug": self.project.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/edit_project.html")

    def test_edit_project_view_post_updates_project_skills_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:edit_project", kwargs={"slug": self.project.slug}),
            data={
                **self.project_data(
                    title="DevConnect Updated",
                    description="Updated description.",
                    status=Project.Status.IN_PROGRESS,
                ),
                "skills": [str(self.django_skill.pk)],
                "new_skills": ["React"],
            },
        )

        self.assertRedirects(response, reverse("portfolio:my_projects"))

        self.project.refresh_from_db()

        self.assertEqual(self.project.title, "DevConnect Updated")
        self.assertEqual(self.project.description, "Updated description.")

        self.assertSetEqual(
            set(self.project.skills.values_list("name", flat=True)),
            {"Django", "React"},
        )

        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.UPDATED,
            ).exists()
        )

    def test_edit_project_view_post_invalid_data_renders_form(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:edit_project", kwargs={"slug": self.project.slug}),
            data=self.project_data(
                title="DevConnect Updated",
                status=Project.Status.COMPLETED,
                live_demo_url="",
                source_code_url="",
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "portfolio/project/edit_project.html")
        self.assertIn("status", response.context["project_form"].errors)

    def test_delete_project_view_post_deletes_project_and_activity(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("portfolio:delete_project", kwargs={"slug": self.project.slug})
        )

        self.assertRedirects(response, reverse("portfolio:my_projects"))
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())
        self.assertTrue(
            Activity.objects.filter(
                user=self.user,
                action=Activity.Action.DELETED,
            ).exists()
        )

    # -------------------------
    # Project images views
    # -------------------------

    def test_manage_project_images_view_get_returns_200(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "portfolio:manage_project_images",
                kwargs={"slug": self.project.slug},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "portfolio/projectimages/manage_project_images.html",
        )

    def test_manage_project_images_view_post_adds_image(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "portfolio:manage_project_images",
                kwargs={"slug": self.project.slug},
            ),
            data={
                "project_images": [build_image_file(name="extra.jpg")],
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "portfolio:manage_project_images",
                kwargs={"slug": self.project.slug},
            ),
        )

        self.assertEqual(self.project.images.count(), 2)

    def test_delete_project_image_view_post_deletes_image(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "portfolio:delete_project_image",
                kwargs={"pk": self.project_image.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "portfolio:manage_project_images",
                kwargs={"slug": self.project.slug},
            ),
        )
        self.assertFalse(ProjectImage.objects.filter(pk=self.project_image.pk).exists())

    def test_edit_project_image_caption_view_post_updates_caption(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "portfolio:edit_project_image_caption",
                kwargs={"pk": self.project_image.pk},
            ),
            data={"caption": "Updated Cover"},
        )

        self.assertRedirects(
            response,
            reverse(
                "portfolio:manage_project_images",
                kwargs={"slug": self.project.slug},
            ),
        )

        self.project_image.refresh_from_db()
        self.assertEqual(self.project_image.caption, "Updated Cover")
