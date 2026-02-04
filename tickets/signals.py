from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Category


@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    """
    Seed a few default categories on first setup.

    Admins can edit/add categories later via Django admin, but this ensures
    the API has sensible values (billing / technical / general) out of the box.
    """
    if sender.name != "tickets":
        return

    for name in ["billing", "technical", "general"]:
        Category.objects.get_or_create(name=name)

