from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from ..models import Activity, MAX_FILE_SIZE, validate_file_size

User = get_user_model()


class ValidateFileSizeTest(TestCase):

    def test_file_smaller_than_limit_is_valid(self):
        file_obj = SimpleUploadedFile(
            name="small.txt",
            content=b"x" * (MAX_FILE_SIZE - 1),
            content_type="text/plain",
        )

        validate_file_size(file_obj)

    def test_file_exactly_at_limit_is_valid(self):
        file_obj = SimpleUploadedFile(
            name="exact.txt",
            content=b"x" * MAX_FILE_SIZE,
            content_type="text/plain",
        )

        validate_file_size(file_obj)

    def test_file_larger_than_limit_raises_validation_error(self):
        file_obj = SimpleUploadedFile(
            name="large.txt",
            content=b"x" * (MAX_FILE_SIZE + 1),
            content_type="text/plain",
        )

        with self.assertRaises(ValidationError):
            validate_file_size(file_obj)


class ActivityModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="amir",
            email="amir@example.com",
            password="StrongPass123!",
        )
        self.target_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="StrongPass123!",
        )

    def test_activity_str_returns_username_and_action(self):
        activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.target_user,
        )

        self.assertEqual(str(activity), "amir - created")

    def test_activity_creates_generic_target_relation(self):
        activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.UPDATED,
            target=self.target_user,
        )

        self.assertEqual(activity.target, self.target_user)
        self.assertEqual(
            activity.target_content_type,
            ContentType.objects.get_for_model(User),
        )
        self.assertEqual(activity.target_object_id, self.target_user.pk)

    def test_activity_timestamps_are_populated(self):
        before_create = timezone.now()

        activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.target_user,
        )

        after_create = timezone.now()

        self.assertIsNotNone(activity.created_at)
        self.assertIsNotNone(activity.updated_at)
        self.assertGreaterEqual(activity.created_at, before_create)
        self.assertLessEqual(activity.created_at, after_create)

    def test_activity_can_be_updated_and_updated_at_changes(self):
        activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.target_user,
        )

        old_updated_at = activity.updated_at

        activity.action = Activity.Action.UPDATED
        activity.save()

        activity.refresh_from_db()

        self.assertEqual(activity.action, Activity.Action.UPDATED)
        self.assertGreaterEqual(activity.updated_at, old_updated_at)

    def test_activity_ordering_is_latest_first(self):
        first = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.target_user,
        )
        second = Activity.objects.create(
            user=self.user,
            action=Activity.Action.UPDATED,
            target=self.target_user,
        )

        activities = list(Activity.objects.all())

        self.assertEqual(activities[0], second)
        self.assertEqual(activities[1], first)

    def test_activity_allows_deleting_target_user_and_keeps_activity_deleted_with_user_cascade(
        self,
    ):
        activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.target_user,
        )

        self.user.delete()

        self.assertFalse(Activity.objects.filter(pk=activity.pk).exists())

    def test_activity_target_is_generic_foreign_key(self):
        activity = Activity.objects.create(
            user=self.user,
            action=Activity.Action.CREATED,
            target=self.target_user,
        )

        fetched = Activity.objects.get(pk=activity.pk)
        self.assertEqual(fetched.target, self.target_user)
