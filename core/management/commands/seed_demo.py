from django.core.management.base import BaseCommand

from core.seed import run


class Command(BaseCommand):
    help = "Load demo catalog data and default users (also runs automatically after migrate)."

    def handle(self, *args, **options):
        run()
        self.stdout.write(self.style.SUCCESS("Seed data loaded."))
