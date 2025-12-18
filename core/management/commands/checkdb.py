from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Check database connectivity by executing SELECT 1"

    def handle(self, *args, **options):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS("[startup] Database connection OK"))
        except Exception as e:
            raise CommandError(f"[startup] Database connection FAILED: {e}")