from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tickets"

    def ready(self):
        # Import signal handlers (e.g. for seeding categories).
        from . import signals  # noqa: F401

