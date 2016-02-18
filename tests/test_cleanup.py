from random import randint

from activities.constants import Action
from activities.constants import Source
from activities.models import Activity
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test.testcases import TestCase
from django_testing.user_utils import create_user

from activities.cleanup import ActivityCleaner


class ActivityCleanupTestCase(TestCase):
    """Testcase for the activity cleanup."""

    def test_cleanup(self):
        """Test the stale activity cleanup."""
        user_content_type = ContentType.objects.get_for_model(
            model=get_user_model()
        )
        user = create_user()
        num_activities = 5
        user_ids = []
        # create activities for non-existent user
        for i in range(5):
            user_id = randint(99999999, 99999999999)
            user_ids.append(user_id)
            Activity.objects.create(about_id=user_id,
                                    about_content_type=user_content_type,
                                    created_user=user,
                                    source=Source.SYSTEM,
                                    action=Action.CREATED)

        # create a real activity about a user that hasn't been deleted
        Activity.objects.create(about_id=user.id,
                                about_content_type=user_content_type,
                                created_user=user,
                                source=Source.SYSTEM,
                                action=Action.CREATED)

        num_activities += 1
        all_user_ids = user_ids + [user.id]
        activity_count = Activity.objects.filter(about_id__in=all_user_ids).count()
        self.assertEqual(activity_count, num_activities)

        cleaner = ActivityCleaner()
        cleaned_objects = cleaner.cleanup(is_dry_run=False)
        cleaned_user_ids = cleaned_objects[user_content_type.model_class()]
        cleaned_user_ids.sort()
        user_ids.sort()
        self.assertListEqual(cleaned_user_ids, user_ids)

        activity_count = Activity.objects.filter(about_id__in=all_user_ids).count()
        self.assertEqual(activity_count, 1)

        for model, cleaned_ids in cleaned_objects.items():
            num_objs = model.objects.filter(id__in=cleaned_ids).count()
            self.assertEqual(num_objs, 0, '{0}: {1}'.format(model, cleaned_ids))
