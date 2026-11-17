from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.common.dev_schema import ensure_sqlite_schema


class Command(BaseCommand):
    help = "Prepara la base de datos de desarrollo (migraciones + esquema SQLite)"

    def handle(self, *args, **options):
        call_command("migrate", interactive=False)
        if ensure_sqlite_schema():
            self.stdout.write(self.style.SUCCESS("Esquema SQLite de desarrollo listo."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "La base no es SQLite; aplicá infrastructure/sql/001_schema.sql."
                )
            )
