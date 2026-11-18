from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection, transaction

MODELOS_CON_SECUENCIA = [
    ("accounts", "Usuario"),
    ("catalog", "Categoria"),
    ("catalog", "Producto"),
    ("catalog", "PrecioProducto"),
    ("sales", "Venta"),
    ("sales", "VentaDetalle"),
    ("purchases", "Proveedor"),
    ("purchases", "Compra"),
    ("purchases", "CompraDetalle"),
    ("catalog", "MovimientoInventario"),
    ("payments", "Pago"),
]


class Command(BaseCommand):
    help = "Carga datos de demostracion desde infrastructure/seed/seed_demo.sql"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="infrastructure/seed/seed_demo.sql",
            help="Ruta al archivo SQL de datos.",
        )

    def handle(self, *args, **options):
        call_command("migrate", interactive=False, verbosity=0)

        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] > 0:
                raise CommandError(
                    "La tabla usuarios ya tiene datos. Usá una base vacía o vaciala antes."
                )

        ruta = Path(options["file"])
        if not ruta.is_absolute():
            ruta = Path(settings.BASE_DIR) / ruta
        if not ruta.exists():
            raise CommandError(f"No existe el archivo SQL: {ruta}")

        sql = ruta.read_text(encoding="utf-8")
        lineas = [
            linea for linea in sql.splitlines() if not linea.strip().startswith("--")
        ]
        sentencias = [
            sentencia.strip()
            for sentencia in "\n".join(lineas).split(";")
            if sentencia.strip()
        ]

        with transaction.atomic():
            with connection.cursor() as cursor:
                for sentencia in sentencias:
                    cursor.execute(sentencia)

            modelos = [
                apps.get_model(app_label, model_name)
                for app_label, model_name in MODELOS_CON_SECUENCIA
            ]
            for sentencia in connection.ops.sequence_reset_sql(no_style(), modelos):
                with connection.cursor() as cursor:
                    cursor.execute(sentencia)

        self.stdout.write(
            self.style.SUCCESS(
                f"Datos de demostracion cargados desde {ruta.name}."
            )
        )
        self.stdout.write(
            "Usuarios: admin1@taller.com / admin2@taller.com / vendedor1..6@taller.com"
        )
        self.stdout.write("Contraseña para todos: Password123!")
