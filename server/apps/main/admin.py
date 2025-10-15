from django.contrib import admin

from server.apps.main.models import BlogPost, DummyModel


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin[BlogPost]):
    """Admin panel example for ``BlogPost`` model."""


# Registrazione DummyModel solo per coverage
admin.site.register(DummyModel)
