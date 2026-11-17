from django.db import models
from django.utils import timezone


class Pago(models.Model):
    METODOS = (
        ("efectivo", "Efectivo"),
        ("transferencia", "Transferencia"),
        ("qr", "QR"),
        ("tarjeta", "Tarjeta"),
        ("otro", "Otro"),
    )

    id = models.AutoField(primary_key=True)
    administrador = models.ForeignKey(
        "accounts.Administrador",
        db_column="administrador_id",
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    venta = models.ForeignKey(
        "sales.Venta",
        db_column="venta_id",
        on_delete=models.CASCADE,
        related_name="pagos",
    )
    metodo = models.CharField(max_length=30, choices=METODOS)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=3, default="BOB")
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "pagos"
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"

    def __str__(self) -> str:
        return f"Pago {self.pk}"
