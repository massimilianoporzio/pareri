"""Tests for the CustomUser model in accounts app."""
# pylint: disable=unused-argument

from typing import final

from django.test import TestCase

from server.apps.accounts.models import CustomUser


@final
class TestCustomUser(TestCase):
    """Basic test to ensure CustomUser can be saved and represented."""

    def test_model_save_and_str(self) -> None:
        """Save a CustomUser and verify id and string representation."""
        user = CustomUser.objects.create_user('case@aslcn1.it')
        user.save()

        assert user.id > 0
        assert isinstance(str(user), str)
