from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import (
    Command as BaseRunserverCommand,
)
from django.core.management import call_command
from django.db import connections

from apps.common.dev_schema import ensure_sqlite_schema


class Command(BaseRunserverCommand):
    def handle(self, *args, **options):
        if settings.DEBUG and connections["default"].vendor == "sqlite":
            call_command("migrate", interactive=False, verbosity=0)
            ensure_sqlite_schema()
        super().handle(*args, **options)
