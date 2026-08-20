from datetime import date
from django.test import TestCase
from accounts.models import Profile, User
from ..forms import EducationForm, ExperienceForm, ProjectForm, SkillForm
from ..models import Experience, Project


class SkillFormTest(TestCase):

    def test_valid_skill_form(self):
        form = SkillForm(
            data={
                "name": "python",
                "icon": "fa-python",
            }
        )

        self.assertTrue(form.is_valid())

    def test_skill_form_missing_name(self):
        form = SkillForm(
            data={
                "name": "",
                "icon": "fa-python",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_skill_form_saves_normalized_name(self):
        form = SkillForm(
            data={
                "name": "   python django   ",
                "icon": "fa-python",
            }
        )

        self.assertTrue(form.is_valid())

        skill = form.save()

        self.assertEqual(skill.name, "Python Django")


class ProjectFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            jop_title="Backend Developer",
            bio="Short bio",
            about="About Amir",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

    def valid_data(self, **overrides):
        data = {
            "title": "DevConnect",
            "description": "Portfolio platform.",
            "status": Project.Status.IN_PROGRESS,
            "live_demo_url": "",
            "source_code_url": "",
            "is_featured": False,
        }
        data.update(overrides)
        return data

    def test_valid_project_form(self):
        form = ProjectForm(data=self.valid_data())

        self.assertTrue(form.is_valid())

    def test_completed_project_without_links_is_invalid(self):
        form = ProjectForm(
            data=self.valid_data(
                status=Project.Status.COMPLETED,
                live_demo_url="",
                source_code_url="",
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("status", form.errors)

    def test_completed_project_with_live_demo_is_valid(self):
        form = ProjectForm(
            data=self.valid_data(
                status=Project.Status.COMPLETED,
                live_demo_url="https://example.com",
            )
        )

        self.assertTrue(form.is_valid())

    def test_completed_project_with_source_code_is_valid(self):
        form = ProjectForm(
            data=self.valid_data(
                status=Project.Status.COMPLETED,
                source_code_url="https://github.com/amir/devconnect",
            )
        )

        self.assertTrue(form.is_valid())


class ExperienceFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            jop_title="Backend Developer",
            bio="Short bio",
            about="About Amir",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

    def valid_data(self, **overrides):
        data = {
            "company_name": "Google",
            "job_title": "Backend Developer",
            "employment_type": Experience.EmploymentType.FULL_TIME,
            "description": "Worked on backend systems.",
            "start_date": date(2024, 1, 1),
            "end_date": date(2025, 1, 1),
            "currently_working": False,
        }
        data.update(overrides)
        return data

    def test_valid_experience_form(self):
        form = ExperienceForm(data=self.valid_data())

        self.assertTrue(form.is_valid())

    def test_currently_working_without_end_date_is_valid(self):
        form = ExperienceForm(
            data=self.valid_data(
                end_date="",
                currently_working=True,
            )
        )

        self.assertTrue(form.is_valid())

    def test_currently_working_with_end_date_is_invalid(self):
        form = ExperienceForm(
            data=self.valid_data(
                currently_working=True,
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_end_date_before_start_date_is_invalid(self):
        form = ExperienceForm(
            data=self.valid_data(
                start_date=date(2025, 1, 1),
                end_date=date(2024, 1, 1),
                currently_working=False,
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)


class EducationFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.profile = Profile.objects.create(
            user=self.user,
            jop_title="Backend Developer",
            bio="Short bio",
            about="About Amir",
            github_url="https://github.com/amir",
            available_for_work=True,
        )

    def valid_data(self, **overrides):
        data = {
            "institution": "Cairo University",
            "degree": "Bachelor",
            "field_of_study": "Computer Science",
            "start_date": date(2020, 1, 1),
            "end_date": date(2024, 1, 1),
            "grade": "Very Good",
            "description": "Studied software engineering.",
        }
        data.update(overrides)
        return data

    def test_valid_education_form(self):
        form = EducationForm(data=self.valid_data())

        self.assertTrue(form.is_valid())

    def test_end_date_before_start_date_is_invalid(self):
        form = EducationForm(
            data=self.valid_data(
                start_date=date(2024, 1, 1),
                end_date=date(2023, 1, 1),
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("end_date", form.errors)

    def test_end_date_equal_start_date_is_valid(self):
        form = EducationForm(
            data=self.valid_data(
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 1),
            )
        )

        self.assertTrue(form.is_valid())
