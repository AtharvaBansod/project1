from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


def seed_after_migrate(sender, **kwargs):
    if getattr(settings, "SEED_ON_MIGRATE", False):
        from .seed import run
        run()


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        post_migrate.connect(seed_after_migrate, sender=self)
