from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from accounts.models import Profile, User
from django.test import TestCase
from datetime import date
from ..models import Skill, Project, ProjectImage, Experience, Education
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image


class SkillModelTest(TestCase):

    def test_skill_strips_and_title_cases_name_on_save(self):
        skill = Skill.objects.create(
            name="   python django   ",
        )

        self.assertEqual(
            skill.name,
            "Python Django",
        )

    def test_skill_str_returns_name(self):
        skill = Skill.objects.create(
            name="python",
        )

        self.assertEqual(
            str(skill),
            "Python",
        )

    def test_skill_name_must_be_unique(self):
        Skill.objects.create(name="Python")

        with self.assertRaises(IntegrityError):
            Skill.objects.create(name="Python")

    def test_skill_icon_is_optional(self):
        skill = Skill.objects.create(
            name="Python",
        )

        self.assertEqual(skill.icon, "")


class ProjectModelTest(TestCase):

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

    def test_project_slug_is_generated_automatically(self):
        project = Project.objects.create(
            profile=self.profile,
            title="My Awesome Project",
            description="A project description.",
        )

        self.assertEqual(
            project.slug,
            "my-awesome-project",
        )

    def test_project_slug_handles_duplicate_slug(self):
        first_project = Project.objects.create(
            profile=self.profile,
            title="My Project",
            description="First project.",
        )

        second_profile_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
        )

        second_profile = Profile.objects.create(
            user=second_profile_user,
            jop_title="Frontend Developer",
            bio="Short bio",
            about="About John",
            github_url="https://github.com/john",
            available_for_work=True,
        )

        second_project = Project.objects.create(
            profile=second_profile,
            title="My Project",
            description="Second project.",
        )

        self.assertEqual(
            first_project.slug,
            "my-project",
        )

        self.assertEqual(
            second_project.slug,
            "my-project-1",
        )

    def test_completed_project_requires_at_least_one_link(self):
        project = Project(
            profile=self.profile,
            title="Completed Project",
            description="Completed project.",
            status=Project.Status.COMPLETED,
        )

        with self.assertRaises(ValidationError):
            project.full_clean()

    def test_completed_project_with_live_demo_is_valid(self):
        project = Project(
            profile=self.profile,
            title="Completed Project",
            slug="completed-project",
            description="Completed project.",
            status=Project.Status.COMPLETED,
            live_demo_url="https://example.com",
        )

        project.full_clean()

    def test_completed_project_with_source_code_is_valid(self):
        project = Project(
            profile=self.profile,
            title="Completed Project",
            slug="completed-project",
            description="Completed project.",
            status=Project.Status.COMPLETED,
            source_code_url="https://github.com/amir/project",
        )

        project.full_clean()

    def test_default_project_status_is_in_progress(self):
        project = Project.objects.create(
            profile=self.profile,
            title="New Project",
            description="Project description.",
        )

        self.assertEqual(
            project.status,
            Project.Status.IN_PROGRESS,
        )

    def test_project_string_representation(self):
        project = Project.objects.create(
            profile=self.profile,
            title="DevConnect",
            description="Portfolio platform.",
        )

        self.assertEqual(
            str(project),
            "DevConnect",
        )

    def test_same_title_is_not_allowed_for_same_profile(self):
        Project.objects.create(
            profile=self.profile,
            title="My Project",
            description="First project.",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Project.objects.bulk_create(
                    [
                        Project(
                            profile=self.profile,
                            title="My Project",
                            slug="another-project",
                            description="Second project.",
                        )
                    ]
                )

    def test_same_title_is_allowed_for_different_profiles(self):
        Project.objects.create(
            profile=self.profile,
            title="My Project",
            description="First project.",
        )

        other_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
        )

        other_profile = Profile.objects.create(
            user=other_user,
            jop_title="Frontend Developer",
            bio="Short bio",
            about="About John",
            github_url="https://github.com/john",
            available_for_work=True,
        )

        project = Project.objects.create(
            profile=other_profile,
            title="My Project",
            description="Second project.",
        )

        self.assertEqual(
            project.title,
            "My Project",
        )

    def test_project_save_runs_model_validation(self):
        project = Project(
            profile=self.profile,
            title="Completed Project",
            description="Completed project.",
            status=Project.Status.COMPLETED,
        )

        with self.assertRaises(ValidationError):
            project.save()


def build_test_image(name="test.jpg", image_format="JPEG"):
    image = Image.new("RGB", (100, 100), "blue")

    buffer = BytesIO()
    image.save(buffer, format=image_format)

    content_type = (
        "image/jpeg"
        if image_format.upper() == "JPEG"
        else f"image/{image_format.lower()}"
    )

    return SimpleUploadedFile(
        name=name,
        content=buffer.getvalue(),
        content_type=content_type,
    )


class ProjectImageModelTest(TestCase):

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

        self.project = Project.objects.create(
            profile=self.profile,
            title="DevConnect",
            description="Portfolio platform.",
        )

    def test_valid_project_image(self):
        image = build_test_image()

        project_image = ProjectImage(
            project=self.project,
            image=image,
        )

        project_image.full_clean()

    def test_invalid_project_image_extension(self):
        image = build_test_image(
            name="test.pdf",
            image_format="JPEG",
        )

        project_image = ProjectImage(
            project=self.project,
            image=image,
        )

        with self.assertRaises(ValidationError):
            project_image.full_clean()

    def test_first_image_gets_display_order_two(self):
        image = ProjectImage.objects.create(
            project=self.project,
            image=build_test_image(),
        )

        self.assertEqual(
            image.display_order,
            2,
        )

    def test_next_image_gets_next_display_order(self):
        first_image = ProjectImage.objects.create(
            project=self.project,
            image=build_test_image(name="first.jpg"),
        )

        second_image = ProjectImage.objects.create(
            project=self.project,
            image=build_test_image(name="second.jpg"),
        )

        self.assertEqual(first_image.display_order, 2)
        self.assertEqual(second_image.display_order, 3)

    def test_duplicate_display_order_is_not_allowed_for_same_project(self):
        ProjectImage.objects.create(
            project=self.project,
            image=build_test_image(),
            display_order=5,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProjectImage.objects.create(
                    project=self.project,
                    image=build_test_image(name="second.jpg"),
                    display_order=5,
                )

    def test_same_display_order_is_allowed_for_different_projects(self):
        other_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
        )

        other_profile = Profile.objects.create(
            user=other_user,
            jop_title="Frontend Developer",
            bio="Short bio",
            about="About John",
            github_url="https://github.com/john",
            available_for_work=True,
        )

        other_project = Project.objects.create(
            profile=other_profile,
            title="Other Project",
            description="Another project.",
        )

        first_image = ProjectImage.objects.create(
            project=self.project,
            image=build_test_image(),
            display_order=5,
        )

        second_image = ProjectImage.objects.create(
            project=other_project,
            image=build_test_image(name="other.jpg"),
            display_order=5,
        )

        self.assertEqual(first_image.display_order, 5)
        self.assertEqual(second_image.display_order, 5)

    def test_project_image_str_with_caption(self):
        project_image = ProjectImage(
            project=self.project,
            image=build_test_image(),
            caption="Homepage",
            display_order=2,
        )

        self.assertEqual(
            str(project_image),
            "DevConnect - Homepage",
        )

    def test_project_image_str_without_caption(self):
        project_image = ProjectImage(
            project=self.project,
            image=build_test_image(),
            display_order=2,
        )

        self.assertEqual(
            str(project_image),
            "DevConnect - Image 2",
        )


class ExperienceModelTest(TestCase):

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

    def test_currently_working_without_end_date_is_valid(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2024, 1, 1),
            end_date=None,
            currently_working=True,
        )

        experience.full_clean()

    def test_currently_working_with_end_date_is_invalid(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2024, 1, 1),
            end_date=date(2025, 1, 1),
            currently_working=True,
        )

        with self.assertRaises(ValidationError):
            experience.full_clean()

    def test_not_currently_working_with_end_date_is_valid(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2024, 1, 1),
            end_date=date(2025, 1, 1),
            currently_working=False,
        )

        experience.full_clean()

    def test_not_currently_working_without_end_date_is_invalid(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2024, 1, 1),
            end_date=None,
            currently_working=False,
        )

        with self.assertRaises(ValidationError):
            experience.full_clean()

    def test_end_date_before_start_date_is_invalid(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2025, 1, 1),
            end_date=date(2024, 1, 1),
            currently_working=False,
        )

        with self.assertRaises(ValidationError):
            experience.full_clean()

    def test_end_date_equal_start_date_is_valid(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1),
            currently_working=False,
        )

        experience.full_clean()

    def test_str_returns_company_and_job_title(self):
        experience = Experience(
            profile=self.profile,
            company_name="Google",
            job_title="Backend Developer",
            employment_type=Experience.EmploymentType.FULL_TIME,
            start_date=date(2024, 1, 1),
            currently_working=True,
        )

        self.assertEqual(
            str(experience),
            "Google - Backend Developer",
        )


class EducationModelTest(TestCase):

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

    def test_education_without_end_date_is_valid(self):
        education = Education(
            profile=self.profile,
            institution="Cairo University",
            degree="BSc",
            field_of_study="Computer Science",
            start_date=date(2020, 1, 1),
            end_date=None,
            grade="A",
            description="Bachelor degree.",
        )

        education.full_clean()

    def test_end_date_equal_start_date_is_valid(self):
        education = Education(
            profile=self.profile,
            institution="Cairo University",
            degree="BSc",
            field_of_study="Computer Science",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
            grade="A",
            description="Bachelor degree.",
        )

        education.full_clean()

    def test_end_date_before_start_date_is_invalid(self):
        education = Education(
            profile=self.profile,
            institution="Cairo University",
            degree="BSc",
            field_of_study="Computer Science",
            start_date=date(2025, 1, 1),
            end_date=date(2024, 1, 1),
            grade="A",
            description="Bachelor degree.",
        )

        with self.assertRaises(ValidationError):
            education.full_clean()

    def test_database_constraint_blocks_end_date_before_start_date(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Education.objects.create(
                    profile=self.profile,
                    institution="Cairo University",
                    degree="BSc",
                    field_of_study="Computer Science",
                    start_date=date(2025, 1, 1),
                    end_date=date(2024, 1, 1),
                    grade="A",
                    description="Bachelor degree.",
                )

    def test_str_returns_institution_and_degree(self):
        education = Education(
            profile=self.profile,
            institution="Cairo University",
            degree="BSc",
            field_of_study="Computer Science",
            start_date=date(2020, 1, 1),
            end_date=date(2024, 1, 1),
            grade="A",
            description="Bachelor degree.",
        )

        self.assertEqual(
            str(education),
            "Cairo University - BSc",
        )
