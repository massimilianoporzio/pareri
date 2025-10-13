from typing import final

from hypothesis import HealthCheck, given, settings
from hypothesis.extra import django

from server.apps.main.models import BlogPost


@final
class TestBlogPost(django.TestCase):
    """This is a property-based test that ensures model correctness."""

    @given(django.from_model(BlogPost))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_model_properties(self, instance: BlogPost) -> None:
        """Tests that instance can be saved and has correct representation."""
        instance.save()

        assert instance.id > 0
        assert len(str(instance)) <= 20
