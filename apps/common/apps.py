from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _asegurar_esquema_sqlite(sender, using, **kwargs) -> None:
    from apps.common.dev_schema import ensure_sqlite_schema

    ensure_sqlite_schema(using=using)


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"
    label = "common"
    verbose_name = "Común"

    def ready(self) -> None:
        post_migrate.connect(
            _asegurar_esquema_sqlite,
            dispatch_uid="apps.common.ensure_sqlite_schema",
        )
